"""Content lifecycle rules, as plain data.

Source of truth: specs/technical/states-events.md (section "Content").
This file has no database or Django imports. Labels and messages are English
identifiers; the web layer translates them (see core/http.py).
"""

from apps.core.enums import LabeledEnum
from apps.core.exceptions import DomainError


class ContentState(LabeledEnum):
    DRAFT = ("draft", "Draft")
    PLANNED = ("planned", "Planned")
    IN_PRODUCTION = ("in_production", "In production")
    INTERNAL_REVIEW = ("internal_review", "Internal review")
    CLIENT_REVIEW = ("client_review", "Waiting for client")
    CHANGES_REQUESTED = ("changes_requested", "Changes requested")
    APPROVED = ("approved", "Approved")
    SCHEDULED = ("scheduled", "Scheduled")
    PUBLISHED = ("published", "Published")
    FAILED = ("failed", "Publishing failed")


class InvalidTransition(DomainError):
    """A state change the lifecycle does not allow."""


# Every change of state that is allowed at all.
ALLOWED_TRANSITIONS = {
    ContentState.DRAFT: {ContentState.PLANNED},
    ContentState.PLANNED: {ContentState.IN_PRODUCTION},
    ContentState.IN_PRODUCTION: {ContentState.INTERNAL_REVIEW},
    ContentState.INTERNAL_REVIEW: {
        ContentState.IN_PRODUCTION,  # rejected internally
        ContentState.CLIENT_REVIEW,  # approved internally, client must approve
        ContentState.APPROVED,  # approved internally, client approval not required
    },
    ContentState.CLIENT_REVIEW: {
        ContentState.APPROVED,
        ContentState.CHANGES_REQUESTED,
        ContentState.INTERNAL_REVIEW,  # edited while the client was reviewing
    },
    ContentState.CHANGES_REQUESTED: {ContentState.IN_PRODUCTION},
    ContentState.APPROVED: {
        ContentState.SCHEDULED,
        ContentState.INTERNAL_REVIEW,  # edited after approval
    },
    ContentState.SCHEDULED: {
        ContentState.PUBLISHED,
        ContentState.FAILED,
        ContentState.APPROVED,  # unscheduled
    },
    ContentState.FAILED: {
        ContentState.SCHEDULED,  # retry
        ContentState.INTERNAL_REVIEW,  # edited after the failure
    },
    ContentState.PUBLISHED: set(),  # final
}

# The moves a person can trigger by hand. Everything else goes through a named
# decision (approve, schedule, ...) that needs its own input.
MANUAL_MOVES = {
    (ContentState.DRAFT, ContentState.PLANNED),
    (ContentState.PLANNED, ContentState.IN_PRODUCTION),
    (ContentState.CHANGES_REQUESTED, ContentState.IN_PRODUCTION),
    (ContentState.IN_PRODUCTION, ContentState.INTERNAL_REVIEW),
}

# What happens when a new version is saved (PRO-013).
RETURNS_TO_INTERNAL_REVIEW_ON_EDIT = {
    ContentState.CLIENT_REVIEW,
    ContentState.APPROVED,
    ContentState.FAILED,
}


def ensure_transition(current, target):
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransition(
            "Cannot change from '{source}' to '{target}'.",
            source=current.label,
            target=target.label,
        )


def ensure_manual_move(current, target):
    if (current, target) not in MANUAL_MOVES:
        raise InvalidTransition(
            "Cannot move from '{source}' to '{target}' by hand.",
            source=current.label,
            target=target.label,
        )


def state_after_edit(current):
    """The state a piece should be in after a new version is saved."""
    if current == ContentState.SCHEDULED:
        raise InvalidTransition("Remove the schedule before editing the content.")
    if current == ContentState.PUBLISHED:
        raise InvalidTransition("Published content cannot be edited.")
    if current in RETURNS_TO_INTERNAL_REVIEW_ON_EDIT:
        return ContentState.INTERNAL_REVIEW
    return current
