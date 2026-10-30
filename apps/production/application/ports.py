"""Ports: what the application needs from the outside world, written as interfaces.

Adapters implement these (production/adapters/ and core/audit.py). Tests use
in-memory fakes (production/tests/fakes.py). The application code never imports
Django.
"""

from typing import Protocol

from apps.production.domain.content import Content


class ContentRepository(Protocol):
    def get(self, organization_id: int, content_id: int) -> Content | None:
        """Load a piece of content, or None if it does not exist in this organization."""

    def save(self, content: Content) -> None:
        """Insert or update. Sets `content.id` on the first save."""

    def client_approval_rule(self, organization_id: int, client_id: int) -> bool | None:
        """Whether the client needs approval. None if the client is not in this organization."""

    def is_internal_member(self, organization_id: int, user_id: int) -> bool:
        """True if the user is a member of the organization and not a client end-user."""


class Notifier(Protocol):
    def notify(
        self,
        *,
        kind: str,
        organization_id: int,
        client_id: int,
        content_id: int,
        title: str,
        owner_id: int | None,
        actor_user_id: int | None,
        event_key: str,
        extra: dict | None = None,
    ) -> list:
        """Tell the people who must know about a content event. Repeated calls with the
        same event_key create nothing new."""


class AuditLog(Protocol):
    def record(
        self,
        *,
        organization_id: int,
        actor_user_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int,
        metadata: dict,
    ) -> None:
        """Append one audit event."""
