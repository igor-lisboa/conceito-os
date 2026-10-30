"""Use cases for content. This is the only way the outside world changes a piece of content.

Every public method follows the same steps:
1. Check the actor's role may do this (capability).
2. Load the piece and check the actor may see it (scope). Out of scope = NotFound.
3. Run the domain method. It raises DomainError if a rule is broken.
4. Save and write the audit events, inside one transaction.

Dependencies come in through the constructor (ports), so tests replace them
with fakes and the Django adapters are plugged in by production/composition.py.
"""

from accounts.permissions import Capability, require_capability
from core.exceptions import DomainError, NotFound
from production.domain.content import Channel, Content, ContentFormat, VersionData
from production.domain.policy import can_access, can_see_client
from production.domain.states import ContentState

ENTITY_TYPE = "ContentItem"


# Which state changes tell someone something, and what kind of notification they send.
NOTIFICATION_KINDS = {
    (ContentState.IN_PRODUCTION.value, ContentState.INTERNAL_REVIEW.value): "internal_review",
    (ContentState.INTERNAL_REVIEW.value, ContentState.CLIENT_REVIEW.value): "client_review",
    (ContentState.CLIENT_REVIEW.value, ContentState.CHANGES_REQUESTED.value): "changes_requested",
    (ContentState.CLIENT_REVIEW.value, ContentState.APPROVED.value): "approved_by_client",
    (ContentState.INTERNAL_REVIEW.value, ContentState.IN_PRODUCTION.value): "internal_rejected",
    (ContentState.SCHEDULED.value, ContentState.FAILED.value): "publish_failed",
}


class ContentService:
    def __init__(self, *, repository, audit, clock, transaction, notifier=None):
        self.repository = repository
        self.audit = audit
        self.clock = clock  # callable returning the current datetime
        self.transaction = transaction  # callable returning a context manager
        self.notifier = notifier  # optional: None disables notifications (used in some tests)

    # --- creating ----------------------------------------------------------

    def create(
        self,
        actor,
        *,
        client_id,
        title,
        channel,
        content_format,
        owner_id=None,
        version=None,
    ):
        require_capability(actor, Capability.CREATE_CONTENT)
        if not can_see_client(actor, client_id):
            raise NotFound("Client not found.")

        approval_required = self.repository.client_approval_rule(actor.organization_id, client_id)
        if approval_required is None:
            raise NotFound("Client not found.")
        if owner_id is not None and not self.repository.is_internal_member(actor.organization_id, owner_id):
            raise DomainError("The person responsible must be a member of the same organization.")

        content = Content.create(
            organization_id=actor.organization_id,
            client_id=client_id,
            owner_id=owner_id,
            title=title,
            channel=Channel(channel),
            content_format=ContentFormat(content_format),
            client_approval_required=approval_required,
            first_version=version or VersionData(),
            created_by_user_id=actor.user_id,
        )
        with self.transaction():
            self.repository.save(content)
            self._audit(actor, content)
        return content.id

    # --- editing and manual moves -----------------------------------------

    def add_version(self, actor, content_id, version):
        require_capability(actor, Capability.EDIT_CONTENT)
        return self._change(actor, content_id, lambda c: c.add_version(version, created_by_user_id=actor.user_id))

    def move_to(self, actor, content_id, target):
        require_capability(actor, Capability.EDIT_CONTENT)
        return self._change(actor, content_id, lambda c: c.move_to(ContentState(target)))

    # --- approvals ---------------------------------------------------------

    def decide_internal(self, actor, content_id, *, approve, comment=""):
        require_capability(actor, Capability.APPROVE_INTERNAL)
        return self._change(
            actor,
            content_id,
            lambda c: c.decide_internal(approve=approve, comment=comment, actor_user_id=actor.user_id),
        )

    def decide_client(self, actor, content_id, *, approve, comment=""):
        require_capability(actor, Capability.CLIENT_APPROVE)
        return self._change(
            actor,
            content_id,
            lambda c: c.decide_client(approve=approve, comment=comment, actor_user_id=actor.user_id),
        )

    # --- scheduling and publishing ----------------------------------------

    def schedule(self, actor, content_id, *, when):
        require_capability(actor, Capability.SCHEDULE_CONTENT)
        return self._change(actor, content_id, lambda c: c.schedule(when, now=self.clock()))

    def unschedule(self, actor, content_id):
        require_capability(actor, Capability.SCHEDULE_CONTENT)
        return self._change(actor, content_id, lambda c: c.unschedule())

    def mark_published(self, actor, content_id, *, url=""):
        require_capability(actor, Capability.SCHEDULE_CONTENT)
        return self._change(actor, content_id, lambda c: c.mark_published(now=self.clock(), url=url))

    def mark_failed(self, actor, content_id, *, reason):
        require_capability(actor, Capability.SCHEDULE_CONTENT)
        return self._change(actor, content_id, lambda c: c.mark_failed(reason))

    # --- internals ---------------------------------------------------------

    def _change(self, actor, content_id, operation):
        content = self._load(actor, content_id)
        with self.transaction():
            operation(content)
            self.repository.save(content)
            self._audit(actor, content)
        return content

    def _load(self, actor, content_id):
        content = self.repository.get(actor.organization_id, content_id)
        if content is None or not can_access(actor, content):
            raise NotFound("Content not found.")
        return content

    def _audit(self, actor, content):
        for event in content.pull_events():
            self.audit.record(
                organization_id=actor.organization_id,
                actor_user_id=actor.user_id,
                action=event.name,
                entity_type=ENTITY_TYPE,
                entity_id=content.id,
                metadata=event.data,
            )
            if event.name == "content.state_changed":
                self._notify(actor, content, event.data)

    def _notify(self, actor, content, change):
        kind = NOTIFICATION_KINDS.get((change["from"], change["to"]))
        if kind is None or self.notifier is None:
            return
        # One notification per event: the same change of the same version is never sent twice.
        event_key = f"{kind}:{content.id}:{len(content.versions)}:{len(content.approvals)}"
        extra = {"reason": change["comment"]} if kind == "publish_failed" else None
        self.notifier.notify(
            kind=kind,
            organization_id=content.organization_id,
            client_id=content.client_id,
            content_id=content.id,
            title=content.title,
            owner_id=content.owner_id,
            actor_user_id=actor.user_id,
            event_key=event_key,
            extra=extra,
        )
