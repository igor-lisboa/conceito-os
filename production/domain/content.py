"""The Content aggregate: one piece of content and everything that happens to it.

DDD terms used here:
- Aggregate root: `Content`. Other code changes a piece only through its methods,
  so the rules below can never be skipped.
- Value objects: `VersionData`, `Version`, `Approval` (frozen, compared by value).
- Domain events: `Content` records what happened in `_events`; the application
  layer reads them with `pull_events()` and writes the audit log.

No database, no Django, no clock: the caller passes in `now` when time matters.
"""

from dataclasses import dataclass, field

from core.enums import LabeledEnum
from core.exceptions import DomainError

from .states import ContentState, ensure_manual_move, ensure_transition, state_after_edit


class Channel(LabeledEnum):
    INSTAGRAM = ("instagram", "Instagram")
    TIKTOK = ("tiktok", "TikTok")


class ContentFormat(LabeledEnum):
    FEED = ("feed", "Feed")
    CAROUSEL = ("carousel", "Carousel")
    REELS = ("reels", "Reels")
    STORY = ("story", "Stories")
    TIKTOK_VIDEO = ("tiktok_video", "TikTok video")


class ApprovalStage(LabeledEnum):
    INTERNAL = ("internal", "Internal review")
    CLIENT = ("client", "Client")


class ApprovalDecision(LabeledEnum):
    APPROVED = ("approved", "Approved")
    CHANGES_REQUESTED = ("changes_requested", "Changes requested")


@dataclass(frozen=True)
class VersionData:
    caption: str = ""
    cta: str = ""
    script: str = ""
    media_url: str = ""


@dataclass(frozen=True)
class Version:
    number: int
    data: VersionData
    created_by_user_id: int | None


@dataclass(frozen=True)
class Approval:
    """A decision tied to the exact version the person saw (PRO-008)."""

    version_number: int
    stage: ApprovalStage
    decision: ApprovalDecision
    comment: str
    actor_user_id: int | None


@dataclass(frozen=True)
class DomainEvent:
    name: str
    data: dict


def _require_text(text, message):
    if not text or not text.strip():
        raise DomainError(message)


@dataclass
class Content:
    organization_id: int
    client_id: int
    title: str
    channel: Channel
    content_format: ContentFormat
    client_approval_required: bool
    owner_id: int | None = None
    state: ContentState = ContentState.DRAFT
    versions: list = field(default_factory=list)
    approvals: list = field(default_factory=list)
    scheduled_for: object = None
    published_at: object = None
    published_url: str = ""
    failure_reason: str = ""
    id: int | None = None  # set by the repository when the piece is first saved
    _events: list = field(default_factory=list, repr=False)

    # --- creation ----------------------------------------------------------

    @classmethod
    def create(cls, *, first_version, created_by_user_id, **fields):
        content = cls(**fields)
        content.versions.append(Version(number=1, data=first_version, created_by_user_id=created_by_user_id))
        content._emit("content.created", {"title": content.title, "client_id": str(content.client_id)})
        return content

    # --- read helpers ------------------------------------------------------

    @property
    def latest_version(self):
        return self.versions[-1]

    def pull_events(self):
        """Return the events recorded since the last call, and clear them."""
        events, self._events = self._events, []
        return events

    # --- editing -----------------------------------------------------------

    def add_version(self, data, *, created_by_user_id):
        """Save a new version. Approved or client-reviewed pieces go back to internal review."""
        new_state = state_after_edit(self.state)
        number = len(self.versions) + 1
        self.versions.append(Version(number=number, data=data, created_by_user_id=created_by_user_id))
        self._emit("content.version_added", {"number": number})

        if new_state != self.state:
            self._change_state(new_state, comment="Content edited; a new review is needed.")

    def move_to(self, target):
        """A manual move between the early stages (see MANUAL_MOVES)."""
        ensure_manual_move(self.state, target)
        self._change_state(target)

    # --- approvals ---------------------------------------------------------

    def decide_internal(self, *, approve, comment, actor_user_id):
        if self.state != ContentState.INTERNAL_REVIEW:
            raise DomainError("This content is not in internal review.")

        if approve:
            target = ContentState.CLIENT_REVIEW if self.client_approval_required else ContentState.APPROVED
        else:
            _require_text(comment, "Explain what needs to change.")
            target = ContentState.IN_PRODUCTION

        self._record_approval(ApprovalStage.INTERNAL, approve, comment, actor_user_id)
        self._change_state(target, comment=comment)

    def decide_client(self, *, approve, comment, actor_user_id):
        if self.state != ContentState.CLIENT_REVIEW:
            raise DomainError("This content is not waiting for your approval.")
        if not approve:
            _require_text(comment, "Explain the changes you need.")

        self._record_approval(ApprovalStage.CLIENT, approve, comment, actor_user_id)
        target = ContentState.APPROVED if approve else ContentState.CHANGES_REQUESTED
        self._change_state(target, comment=comment)

    # --- scheduling and publishing ----------------------------------------

    def schedule(self, when, *, now):
        if when is None:
            raise DomainError("Enter the publishing date.")
        if when <= now:
            raise DomainError("The publishing date must be in the future.")
        self._change_state(ContentState.SCHEDULED, scheduled_for=when, failure_reason="")

    def unschedule(self):
        self._change_state(ContentState.APPROVED, scheduled_for=None)

    def mark_published(self, *, now, url=""):
        """The team posted the piece by hand. The link, when given, is kept as proof."""
        self._change_state(ContentState.PUBLISHED, published_at=now, published_url=url.strip())

    def mark_failed(self, reason):
        """A failure stays visible as failed. It is never recorded as published."""
        _require_text(reason, "Describe the publishing failure.")
        self._change_state(ContentState.FAILED, comment=reason, failure_reason=reason)

    # --- internals ---------------------------------------------------------

    def _change_state(self, target, *, comment="", **fields):
        ensure_transition(self.state, target)
        previous = self.state
        self.state = target
        for name, value in fields.items():
            setattr(self, name, value)
        self._emit(
            "content.state_changed",
            {"from": previous.value, "to": target.value, "comment": comment},
        )

    def _record_approval(self, stage, approve, comment, actor_user_id):
        decision = ApprovalDecision.APPROVED if approve else ApprovalDecision.CHANGES_REQUESTED
        approval = Approval(
            version_number=self.latest_version.number,
            stage=stage,
            decision=decision,
            comment=comment,
            actor_user_id=actor_user_id,
        )
        self.approvals.append(approval)
        self._emit(
            "content.approval_recorded",
            {"stage": stage.value, "decision": decision.value, "version": approval.version_number},
        )

    def _emit(self, name, data):
        self._events.append(DomainEvent(name=name, data=data))
