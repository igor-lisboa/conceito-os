"""Behavior of the Content aggregate. These are the business rules of the product.

They map to specs/modules/production-approval.md and specs/technical/states-events.md.
"""

from datetime import UTC, datetime, timedelta
from unittest import TestCase

from core.exceptions import DomainError
from production.domain.content import (
    ApprovalDecision,
    ApprovalStage,
    Channel,
    Content,
    ContentFormat,
    VersionData,
)
from production.domain.states import ContentState, InvalidTransition

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
LATER = NOW + timedelta(days=1)
REVIEWER = 10
CLIENT_USER = 20


def new_content(client_approval_required=True):
    return Content.create(
        organization_id=1,
        client_id=5,
        owner_id=7,
        title="Post de terça",
        channel=Channel.INSTAGRAM,
        content_format=ContentFormat.CAROUSEL,
        client_approval_required=client_approval_required,
        first_version=VersionData(caption="Legenda v1"),
        created_by_user_id=7,
    )


def move_to_internal_review(content):
    content.move_to(ContentState.PLANNED)
    content.move_to(ContentState.IN_PRODUCTION)
    content.move_to(ContentState.INTERNAL_REVIEW)


def approve_everything(content):
    move_to_internal_review(content)
    content.decide_internal(approve=True, comment="", actor_user_id=REVIEWER)
    content.decide_client(approve=True, comment="", actor_user_id=CLIENT_USER)


class CreationTests(TestCase):
    def test_new_content_starts_as_draft_with_one_version(self):
        content = new_content()

        self.assertEqual(content.state, ContentState.DRAFT)
        self.assertEqual(len(content.versions), 1)
        self.assertEqual(content.latest_version.number, 1)
        self.assertEqual(content.latest_version.data.caption, "Legenda v1")

    def test_creation_emits_an_event(self):
        content = new_content()
        self.assertEqual([event.name for event in content.pull_events()], ["content.created"])

    def test_pull_events_clears_the_queue(self):
        content = new_content()
        content.pull_events()
        self.assertEqual(content.pull_events(), [])


class HappyPathTests(TestCase):
    def test_full_lifecycle_with_client_approval_reaches_published(self):
        content = new_content(client_approval_required=True)

        content.move_to(ContentState.PLANNED)
        content.move_to(ContentState.IN_PRODUCTION)
        content.move_to(ContentState.INTERNAL_REVIEW)
        content.decide_internal(approve=True, comment="", actor_user_id=REVIEWER)
        self.assertEqual(content.state, ContentState.CLIENT_REVIEW)

        content.decide_client(approve=True, comment="", actor_user_id=CLIENT_USER)
        self.assertEqual(content.state, ContentState.APPROVED)

        content.schedule(LATER, now=NOW)
        self.assertEqual(content.state, ContentState.SCHEDULED)
        self.assertEqual(content.scheduled_for, LATER)

        content.mark_published(now=LATER)
        self.assertEqual(content.state, ContentState.PUBLISHED)
        self.assertEqual(content.published_at, LATER)

    def test_every_change_is_recorded_as_an_event_in_order(self):
        content = new_content()
        content.pull_events()

        content.move_to(ContentState.PLANNED)
        content.move_to(ContentState.IN_PRODUCTION)

        events = content.pull_events()
        self.assertEqual([e.name for e in events], ["content.state_changed", "content.state_changed"])
        self.assertEqual(events[0].data["from"], "draft")
        self.assertEqual(events[0].data["to"], "planned")
        self.assertEqual(events[1].data["to"], "in_production")


class InternalReviewTests(TestCase):
    def test_internal_approval_skips_client_when_not_required(self):
        content = new_content(client_approval_required=False)
        move_to_internal_review(content)

        content.decide_internal(approve=True, comment="", actor_user_id=REVIEWER)

        self.assertEqual(content.state, ContentState.APPROVED)

    def test_internal_rejection_needs_a_comment(self):
        content = new_content()
        move_to_internal_review(content)

        with self.assertRaises(DomainError):
            content.decide_internal(approve=False, comment="   ", actor_user_id=REVIEWER)
        self.assertEqual(content.state, ContentState.INTERNAL_REVIEW)
        self.assertEqual(content.approvals, [])

    def test_internal_rejection_returns_to_production_and_keeps_the_comment(self):
        content = new_content()
        move_to_internal_review(content)

        content.decide_internal(approve=False, comment="Trocar a foto", actor_user_id=REVIEWER)

        self.assertEqual(content.state, ContentState.IN_PRODUCTION)
        self.assertEqual(content.approvals[-1].comment, "Trocar a foto")
        self.assertEqual(content.approvals[-1].decision, ApprovalDecision.CHANGES_REQUESTED)

    def test_approval_is_tied_to_the_version_that_was_reviewed(self):
        content = new_content()
        move_to_internal_review(content)

        content.decide_internal(approve=True, comment="", actor_user_id=REVIEWER)

        approval = content.approvals[0]
        self.assertEqual(approval.version_number, 1)
        self.assertEqual(approval.stage, ApprovalStage.INTERNAL)
        self.assertEqual(approval.actor_user_id, REVIEWER)

    def test_cannot_decide_internally_outside_internal_review(self):
        content = new_content()
        with self.assertRaises(DomainError):
            content.decide_internal(approve=True, comment="", actor_user_id=REVIEWER)


class ClientReviewTests(TestCase):
    def test_client_cannot_decide_before_the_piece_reaches_them(self):
        content = new_content()
        with self.assertRaises(DomainError):
            content.decide_client(approve=True, comment="", actor_user_id=CLIENT_USER)

    def test_requesting_changes_needs_a_comment(self):
        content = new_content()
        move_to_internal_review(content)
        content.decide_internal(approve=True, comment="", actor_user_id=REVIEWER)

        with self.assertRaises(DomainError):
            content.decide_client(approve=False, comment="", actor_user_id=CLIENT_USER)
        self.assertEqual(content.state, ContentState.CLIENT_REVIEW)

    def test_changes_requested_by_client_can_go_back_to_production(self):
        content = new_content()
        move_to_internal_review(content)
        content.decide_internal(approve=True, comment="", actor_user_id=REVIEWER)
        content.decide_client(approve=False, comment="Mais leve, por favor", actor_user_id=CLIENT_USER)
        self.assertEqual(content.state, ContentState.CHANGES_REQUESTED)

        content.move_to(ContentState.IN_PRODUCTION)

        self.assertEqual(content.state, ContentState.IN_PRODUCTION)


class EditingTests(TestCase):
    def test_editing_an_approved_piece_sends_it_back_to_internal_review(self):
        content = new_content()
        approve_everything(content)

        content.add_version(VersionData(caption="Legenda v2"), created_by_user_id=7)

        self.assertEqual(content.state, ContentState.INTERNAL_REVIEW)
        self.assertEqual(content.latest_version.number, 2)

    def test_old_approval_still_points_to_the_version_that_was_approved(self):
        # PRO-008: after an edit, the record must still show what was approved.
        content = new_content()
        approve_everything(content)
        content.add_version(VersionData(caption="Legenda v2"), created_by_user_id=7)

        approved_versions = [a.version_number for a in content.approvals]
        self.assertEqual(approved_versions, [1, 1])

    def test_editing_a_draft_keeps_its_state(self):
        content = new_content()
        content.add_version(VersionData(caption="Rascunho 2"), created_by_user_id=7)
        self.assertEqual(content.state, ContentState.DRAFT)

    def test_scheduled_piece_cannot_be_edited(self):
        content = new_content()
        approve_everything(content)
        content.schedule(LATER, now=NOW)

        with self.assertRaises(InvalidTransition):
            content.add_version(VersionData(caption="Mudança"), created_by_user_id=7)
        self.assertEqual(len(content.versions), 1)


class SchedulingTests(TestCase):
    def test_scheduling_requires_a_date(self):
        content = new_content()
        approve_everything(content)
        with self.assertRaises(DomainError):
            content.schedule(None, now=NOW)

    def test_scheduling_in_the_past_is_refused(self):
        content = new_content()
        approve_everything(content)
        with self.assertRaises(DomainError):
            content.schedule(NOW - timedelta(minutes=1), now=NOW)
        self.assertEqual(content.state, ContentState.APPROVED)

    def test_unschedule_returns_to_approved_and_clears_the_date(self):
        content = new_content()
        approve_everything(content)
        content.schedule(LATER, now=NOW)

        content.unschedule()

        self.assertEqual(content.state, ContentState.APPROVED)
        self.assertIsNone(content.scheduled_for)

    def test_an_unapproved_piece_cannot_be_scheduled(self):
        content = new_content()
        move_to_internal_review(content)
        with self.assertRaises(InvalidTransition):
            content.schedule(LATER, now=NOW)


class FailureTests(TestCase):
    def test_failure_needs_a_reason_and_is_never_published(self):
        content = new_content()
        approve_everything(content)
        content.schedule(LATER, now=NOW)

        with self.assertRaises(DomainError):
            content.mark_failed("  ")
        self.assertEqual(content.state, ContentState.SCHEDULED)

        content.mark_failed("Token da rede expirou")
        self.assertEqual(content.state, ContentState.FAILED)
        self.assertEqual(content.failure_reason, "Token da rede expirou")
        self.assertIsNone(content.published_at)

    def test_failed_piece_can_be_rescheduled_and_clears_the_reason(self):
        content = new_content()
        approve_everything(content)
        content.schedule(LATER, now=NOW)
        content.mark_failed("Erro temporário")

        content.schedule(LATER + timedelta(hours=1), now=NOW)

        self.assertEqual(content.state, ContentState.SCHEDULED)
        self.assertEqual(content.failure_reason, "")


class FinalStateTests(TestCase):
    def published_content(self):
        content = new_content()
        approve_everything(content)
        content.schedule(LATER, now=NOW)
        content.mark_published(now=LATER)
        return content

    def test_published_piece_cannot_be_edited(self):
        with self.assertRaises(InvalidTransition):
            self.published_content().add_version(VersionData(caption="x"), created_by_user_id=7)

    def test_published_piece_cannot_be_scheduled_again(self):
        with self.assertRaises(InvalidTransition):
            self.published_content().schedule(LATER + timedelta(days=1), now=NOW)
