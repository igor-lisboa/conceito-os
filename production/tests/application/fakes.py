"""In-memory replacements for the ports. They behave like the real adapters
for the purposes of the application tests, and they keep no database state."""

import contextlib
from datetime import UTC, datetime

from accounts.roles import Role
from core.actor import Actor
from production.application.content_service import ContentService
from production.domain.content import Channel, ContentFormat

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


class InMemoryContentRepository:
    def __init__(self):
        self.rows = {}
        self._next_id = 1
        self.client_rules = {}  # (organization_id, client_id) -> approval required
        self.internal_members = set()  # (organization_id, user_id)

    def get(self, organization_id, content_id):
        content = self.rows.get(content_id)
        if content is None or content.organization_id != organization_id:
            return None
        return content

    def save(self, content):
        if content.id is None:
            content.id = self._next_id
            self._next_id += 1
        self.rows[content.id] = content

    def client_approval_rule(self, organization_id, client_id):
        return self.client_rules.get((organization_id, client_id))

    def is_internal_member(self, organization_id, user_id):
        return (organization_id, user_id) in self.internal_members


class RecordingAuditLog:
    def __init__(self):
        self.events = []

    def record(self, **event):
        self.events.append(event)

    def actions(self):
        return [event["action"] for event in self.events]


def actor(role, user_id, *, organization_id=1, client_ids=(), sees_all=False):
    return Actor(
        user_id=user_id,
        organization_id=organization_id,
        role=role.value,
        sees_all_clients=sees_all,
        sees_only_assigned=role == Role.FREELANCER,
        client_ids=frozenset(client_ids),
    )


class Harness:
    """A ContentService wired to fakes, plus the fakes so tests can inspect them."""

    CLIENT_ID = 5
    ORGANIZATION_ID = 1

    def __init__(self):
        self.repository = InMemoryContentRepository()
        self.audit = RecordingAuditLog()
        self.service = ContentService(
            repository=self.repository,
            audit=self.audit,
            clock=lambda: NOW,
            transaction=contextlib.nullcontext,
        )
        self.repository.client_rules[(self.ORGANIZATION_ID, self.CLIENT_ID)] = True
        self.repository.internal_members.add((self.ORGANIZATION_ID, 2))  # a team member

    def owner(self):
        return actor(Role.OWNER, 1, sees_all=True)

    def create(self, creator, *, owner_id=None, client_id=CLIENT_ID):
        return self.service.create(
            creator,
            client_id=client_id,
            title="Post",
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            owner_id=owner_id,
        )
