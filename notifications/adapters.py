"""Django adapter for the Notifier port: decides who gets a notification and writes it.

The application layer says WHAT happened (for example "the client was asked to
approve piece 12"). This module decides WHO must know, using the same visibility
rules as the rest of the app, and records one notification per person.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.urls import reverse

from accounts.models import Membership
from accounts.roles import Role
from clients.models import Client

from .models import KIND_MESSAGES, Notification

logger = logging.getLogger(__name__)

CLIENT_KINDS = {"client_review"}
REJECTION_KINDS = {"internal_rejected"}


def _recipient_memberships(kind, *, organization_id, client_id, owner_id, actor_user_id):
    """Memberships that must hear about this event, without the person who caused it."""
    if kind in CLIENT_KINDS:
        # The end client(s) with access to this brand.
        memberships = Membership.objects.filter(
            organization_id=organization_id,
            role=Role.CLIENT.value,
            client_accesses__client_id=client_id,
        )
    elif kind in REJECTION_KINDS and owner_id is not None:
        # Sent back to the person who made the piece.
        memberships = Membership.objects.filter(organization_id=organization_id, user_id=owner_id)
    else:
        # Owners see everything; account managers see the brands they were given.
        memberships = Membership.objects.filter(organization_id=organization_id).filter(
            Q(role=Role.OWNER.value)
            | Q(role=Role.ACCOUNT_MANAGER.value, client_accesses__client_id=client_id)
        )
    return memberships.exclude(user_id=actor_user_id).select_related("user").distinct()


class DjangoNotifier:
    def notify(
        self,
        *,
        kind,
        organization_id,
        client_id,
        content_id,
        title,
        owner_id,
        actor_user_id,
        event_key,
        extra=None,
    ):
        client_name = Client.objects.filter(pk=client_id).values_list("name", flat=True).first() or ""
        params = {"title": title, "client": client_name, **(extra or {})}
        url = reverse("portal_detail", args=[content_id]) if kind in CLIENT_KINDS else reverse(
            "content_detail", args=[content_id]
        )
        if kind not in KIND_MESSAGES:
            raise ValueError(f"Unknown notification kind: {kind}")

        created = []
        for membership in _recipient_memberships(
            kind,
            organization_id=organization_id,
            client_id=client_id,
            owner_id=owner_id,
            actor_user_id=actor_user_id,
        ):
            notification, was_created = Notification.objects.get_or_create(
                recipient=membership.user,
                event_key=event_key,
                defaults={
                    "organization_id": organization_id,
                    "kind": kind,
                    "params": params,
                    "url": url,
                },
            )
            if was_created:
                created.append(notification)

        for notification in created:
            transaction.on_commit(lambda n=notification: _send_email(n))
        return created

    def notify_users(
        self, *, users, kind, organization_id, content_id, title, actor_user_id, event_key, extra=None
    ):
        """Notify a given list of people (used for mentions, where the recipients are named in the text)."""
        if kind not in KIND_MESSAGES:
            raise ValueError(f"Unknown notification kind: {kind}")
        params = {"title": title, **(extra or {})}
        url = reverse("content_detail", args=[content_id])

        created = []
        for user in users:
            if user.pk == actor_user_id:
                continue
            notification, was_created = Notification.objects.get_or_create(
                recipient=user,
                event_key=event_key,
                defaults={"organization_id": organization_id, "kind": kind, "params": params, "url": url},
            )
            if was_created:
                created.append(notification)
        for notification in created:
            transaction.on_commit(lambda n=notification: _send_email(n))
        return created


def _send_email(notification):
    """Email copy of a notification. A failed send is logged; the in-app notification stays."""
    if not notification.recipient.email:
        return
    message = notification.message
    body = f"{message}\n\n{settings.SITE_URL}{notification.url}\n\n-- Conceito OS"
    try:
        send_mail(f"Conceito OS: {message}", body, settings.DEFAULT_FROM_EMAIL, [notification.recipient.email])
    except Exception:
        logger.exception("Could not email notification %s", notification.pk)
