"""Team management: invite people by email and remove their access.

Invitations reuse Django's password reset machinery: the invited person gets a link
to set their own password. Removing a membership takes effect on the very next
request, because the membership is looked up on every request (accounts/middleware.py).

These functions take the acting Membership (this is the simple style used by
accounts and clients; see docs/architecture.md).
"""

import logging

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

from .models import Membership
from .permissions import Capability, require_capability
from .roles import Role
from .sessions import end_user_sessions

User = get_user_model()
logger = logging.getLogger(__name__)

MEMBER_INVITED = "member.invited"
MEMBER_REMOVED = "member.removed"
INVITATION_LANGUAGE = "pt-br"


@transaction.atomic
def invite_member(membership, *, email, role, client_ids=()):
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

    invited = Membership.objects.create(user=user, organization=organization, role=role)

    clients = Client.objects.filter(organization=organization, archived_at__isnull=True, pk__in=client_ids)
    for client in clients:
        ClientAccess.objects.create(organization=organization, client=client, membership=invited)

    record_event(
        organization=organization,
        actor=membership.user,
        action=MEMBER_INVITED,
        entity=invited,
        metadata={"role": role, "clients": sorted(str(c.pk) for c in clients)},
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
