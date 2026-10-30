"""Composition root: the one place where ports are wired to Django adapters.

Views call build_content_service() and get a ready-to-use service. Nothing else
needs to know which database, clock, transaction or notifier is in use.
"""

from django.db import transaction
from django.utils import timezone

from core.audit import DjangoAuditLog
from notifications.adapters import DjangoNotifier

from .adapters.django_repository import DjangoContentRepository
from .application.content_service import ContentService


def build_content_service():
    return ContentService(
        repository=DjangoContentRepository(),
        audit=DjangoAuditLog(),
        clock=timezone.now,
        transaction=transaction.atomic,
        notifier=DjangoNotifier(),
    )
