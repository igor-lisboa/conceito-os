"""Team management: invite people by email and remove their access.

Invitations reuse Django's password reset machinery: the invited person gets a link
to set their own password. Removing a membership takes effect on the very next
request, because the membership is looked up on every request (accounts/middleware.py).

These functions take the acting Membership (this is the simple style used by
accounts and clients; see docs/architecture.md).
"""

import logging
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.clients.models import Client, ClientAccess
from apps.core.audit import record_event
from apps.core.exceptions import DomainError

from .models import Membership, MFADevice
from .permissions import Capability, require_capability
from .roles import Role
from .sessions import end_user_sessions

User = get_user_model()
logger = logging.getLogger(__name__)

MEMBER_INVITED = "member.invited"
MEMBER_REMOVED = "member.removed"
MEMBER_ANONYMIZED = "person.anonymized"
MEMBER_CRM_ACCESS_CHANGED = "member.crm_access_changed"
INVITATION_LANGUAGE = "pt-br"
# Anonymized accounts get an address in a reserved domain, so they can never receive mail.
ANONYMOUS_DOMAIN = "anonymized.invalid"


@transaction.atomic
def invite_member(membership, *, email, role, client_ids=(), crm_access=False):
    """Add a person to the organization. Creates the account if the email is new."""
    require_capability(membership, Capability.MANAGE_TEAM)
    email = email.strip().lower()
    organization = membership.organization

    user = User.objects.filter(email=email).first()
    if user is None:
        user = User(username=email, email=email)
        user.set_unusable_password()  # the invited person sets their own password
        user.save()
    elif Membership.objects.filter(user=user, organization=organization).exists():
        raise DomainError("This person is already a member of this organization.")

    invited = _restore_or_create_membership(user, organization, role, crm_access)

    clients = Client.objects.filter(organization=organization, archived_at__isnull=True, pk__in=client_ids)
    for client in clients:
        _restore_or_create_access(organization, client, invited)

    record_event(
        organization=organization,
        actor=membership.user,
        action=MEMBER_INVITED,
        entity=invited,
        metadata={"role": role, "crm_access": bool(crm_access), "clients": sorted(str(c.pk) for c in clients)},
    )
    transaction.on_commit(lambda: send_invitation_email(user, organization.name))
    return invited


@transaction.atomic
def remove_member(membership, target):
    """Remove a person's access to the organization. Their account and history stay."""
    require_capability(membership, Capability.MANAGE_TEAM)
    organization = membership.organization
    if target.organization_id != organization.pk:
        raise DomainError("This membership belongs to another organization.")
    if target.user_id == membership.user_id:
        raise DomainError("You cannot remove your own access.")
    if target.role == Role.OWNER.value and _owner_count(organization) <= 1:
        raise DomainError("The last owner of the organization cannot be removed.")

    record_event(
        organization=organization,
        actor=membership.user,
        action=MEMBER_REMOVED,
        entity=target,
        metadata={"email": target.user.email, "role": target.role},
    )
    ClientAccess.objects.filter(membership=target).delete()
    target.delete()
    # The person's open browsers stop working at once (AUTH-012). Their account stays.
    end_user_sessions(target.user)


def _restore_or_create_membership(user, organization, role, crm_access=False):
    """A removed person who is invited again gets their old membership back (soft delete, DAT-007).

    The unique (user, organization) constraint allows one row, so the removed row is reused.
    """
    former = Membership.all_objects.filter(user=user, organization=organization).first()
    if former is None:
        return Membership.objects.create(
            user=user, organization=organization, role=role, crm_access=crm_access
        )
    former.role = role
    former.crm_access = crm_access
    former.deleted_at = None
    former.save(update_fields=["role", "crm_access", "deleted_at"])
    return former


@transaction.atomic
def set_crm_access(membership, target, *, allowed):
    """Owner grants or removes CRM access for one person (D-16, answer 4B)."""
    require_capability(membership, Capability.MANAGE_TEAM)
    if target.organization_id != membership.organization_id:
        raise DomainError("This membership belongs to another organization.")
    if target.deleted_at is not None:
        raise DomainError("This person has no access to the organization.")
    if target.crm_access == allowed:
        return target
    target.crm_access = allowed
    target.save(update_fields=["crm_access"])
    record_event(
        organization=membership.organization,
        actor=membership.user,
        action=MEMBER_CRM_ACCESS_CHANGED,
        entity=target,
        metadata={"crm_access": allowed},
    )
    return target


def _restore_or_create_access(organization, client, membership):
    access = ClientAccess.all_objects.filter(client=client, membership=membership).first()
    if access is None:
        ClientAccess.objects.create(organization=organization, client=client, membership=membership)
    elif access.deleted_at is not None:
        access.deleted_at = None
        access.save(update_fields=["deleted_at"])


@transaction.atomic
def anonymize_member(membership, target):
    """Replace a removed person's personal data with an anonymous marker (DAT-011, D-17).

    The records stay: their comments, approvals and audit events keep pointing at the same
    account, which no longer shows a name or an email. Only a person whose access was removed
    can be anonymized, so an active person's data is never changed by mistake.
    """
    require_capability(membership, Capability.MANAGE_TEAM)
    organization = membership.organization
    if target.organization_id != organization.pk:
        raise DomainError("This membership belongs to another organization.")
    if target.deleted_at is None:
        raise DomainError("Remove this person's access before anonymizing their data.")
    user = target.user
    if user.email.endswith("@" + ANONYMOUS_DOMAIN):
        return target  # already anonymized

    marker = f"anonymous-{uuid.uuid4().hex[:12]}"
    user.email = f"{marker}@{ANONYMOUS_DOMAIN}"
    user.username = marker
    user.first_name = ""
    user.last_name = ""
    user.is_active = False
    user.set_unusable_password()
    user.save()
    # The authenticator stays encrypted, but it is switched off so it can never be used.
    MFADevice.objects.filter(user=user).update(confirmed=False)

    record_event(
        organization=organization,
        actor=membership.user,
        action=MEMBER_ANONYMIZED,
        entity=target,
        metadata={"role": target.role},
    )
    return target


def _owner_count(organization):
    return Membership.objects.filter(organization=organization, role=Role.OWNER.value).count()


def send_invitation_email(user, organization_name):
    """Email the set-password link. A failed send is logged; the invitation stays valid."""
    with translation.override(INVITATION_LANGUAGE):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        context = {
            "organization": organization_name,
            "link": f"{settings.SITE_URL}{reverse('password_reset_confirm', args=[uid, token])}",
        }
        subject = render_to_string("emails/invite_subject.txt", context).strip()
        body = render_to_string("emails/invite.txt", context)
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
    except Exception:
        logger.exception("Could not send the invitation to user %s", user.pk)
