"""Rules of the content lifecycle as data. No database, no Django: runs in milliseconds."""

from unittest import TestCase

from core.exceptions import DomainError
from production.domain.states import (
    ALLOWED_TRANSITIONS,
    MANUAL_MOVES,
    ContentState,
    InvalidTransition,
    ensure_manual_move,
    ensure_transition,
    state_after_edit,
)


class TransitionTableTests(TestCase):
    def test_every_state_has_an_entry(self):
        self.assertEqual(set(ALLOWED_TRANSITIONS), set(ContentState))

    def test_targets_are_real_states(self):
        for targets in ALLOWED_TRANSITIONS.values():
            self.assertTrue(targets <= set(ContentState))

    def test_published_is_final(self):
        self.assertEqual(ALLOWED_TRANSITIONS[ContentState.PUBLISHED], set())

    def test_manual_moves_are_a_subset_of_allowed_transitions(self):
        # A manual move that the table forbids would be a bug in the rules.
        for current, target in MANUAL_MOVES:
            self.assertIn(target, ALLOWED_TRANSITIONS[current], f"{current} -> {target}")

    def test_publishing_only_comes_from_scheduled(self):
        sources = [s for s, targets in ALLOWED_TRANSITIONS.items() if ContentState.PUBLISHED in targets]
        self.assertEqual(sources, [ContentState.SCHEDULED])

    def test_scheduling_only_comes_from_approved_or_failed(self):
        sources = {s for s, targets in ALLOWED_TRANSITIONS.items() if ContentState.SCHEDULED in targets}
        self.assertEqual(sources, {ContentState.APPROVED, ContentState.FAILED})


class EnsureTransitionTests(TestCase):
    def test_allowed_transition_passes(self):
        ensure_transition(ContentState.APPROVED, ContentState.SCHEDULED)

    def test_skipping_review_is_refused(self):
        with self.assertRaises(InvalidTransition):
            ensure_transition(ContentState.DRAFT, ContentState.APPROVED)

    def test_scheduling_a_draft_is_refused(self):
        with self.assertRaises(InvalidTransition):
            ensure_transition(ContentState.DRAFT, ContentState.SCHEDULED)

    def test_invalid_transition_is_a_domain_error_with_a_readable_english_message(self):
        with self.assertRaises(DomainError) as context:
            ensure_transition(ContentState.PUBLISHED, ContentState.DRAFT)
        self.assertEqual(str(context.exception), "Cannot change from 'Published' to 'Draft'.")
        self.assertEqual(context.exception.message, "Cannot change from '{source}' to '{target}'.")


class ManualMoveTests(TestCase):
    def test_draft_can_be_planned_by_hand(self):
        ensure_manual_move(ContentState.DRAFT, ContentState.PLANNED)

    def test_internal_review_cannot_be_left_by_hand(self):
        # Leaving internal review needs a decision with a comment, never a plain move.
        with self.assertRaises(InvalidTransition):
            ensure_manual_move(ContentState.INTERNAL_REVIEW, ContentState.IN_PRODUCTION)

    def test_client_review_cannot_be_skipped_by_hand(self):
        with self.assertRaises(InvalidTransition):
            ensure_manual_move(ContentState.INTERNAL_REVIEW, ContentState.APPROVED)


class StateAfterEditTests(TestCase):
    def test_draft_stays_draft(self):
        self.assertEqual(state_after_edit(ContentState.DRAFT), ContentState.DRAFT)

    def test_approved_goes_back_to_internal_review(self):
        self.assertEqual(state_after_edit(ContentState.APPROVED), ContentState.INTERNAL_REVIEW)

    def test_client_review_goes_back_to_internal_review(self):
        self.assertEqual(state_after_edit(ContentState.CLIENT_REVIEW), ContentState.INTERNAL_REVIEW)

    def test_scheduled_content_cannot_be_edited(self):
        with self.assertRaises(InvalidTransition):
            state_after_edit(ContentState.SCHEDULED)

    def test_published_content_cannot_be_edited(self):
        with self.assertRaises(InvalidTransition):
            state_after_edit(ContentState.PUBLISHED)
