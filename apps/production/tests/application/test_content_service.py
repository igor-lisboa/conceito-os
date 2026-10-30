"""Use cases for content, tested with in-memory fakes (no database).

Each test describes one rule a user can run into. Permission problems raise
Forbidden, and content outside the user's scope raises NotFound.
"""

from datetime import timedelta
from unittest import TestCase

from apps.accounts.roles import Role
from apps.core.exceptions import DomainError, Forbidden, NotFound
from apps.production.domain.content import VersionData
from apps.production.domain.states import ContentState

from .fakes import NOW, Harness, actor


class CreateContentTests(TestCase):
    def setUp(self):
        self.h = Harness()

    def test_creative_creates_content_in_draft_and_audits_it(self):
        creative = actor(Role.CREATIVE, 3, client_ids={Harness.CLIENT_ID})

        content_id = self.h.create(creative)

        content = self.h.repository.rows[content_id]
        self.assertEqual(content.state, ContentState.DRAFT)
        self.assertEqual(self.h.audit.actions(), ["content.created"])
        self.assertEqual(self.h.audit.events[0]["actor_user_id"], 3)
        self.assertEqual(self.h.audit.events[0]["organization_id"], Harness.ORGANIZATION_ID)

    def test_freelancer_cannot_create_content(self):
        freelancer = actor(Role.FREELANCER, 4, client_ids={Harness.CLIENT_ID})
        with self.assertRaises(Forbidden):
            self.h.create(freelancer)
        self.assertEqual(self.h.repository.rows, {})

    def test_creating_for_a_client_outside_scope_looks_like_not_found(self):
        manager = actor(Role.ACCOUNT_MANAGER, 3, client_ids={99})
        with self.assertRaises(NotFound):
            self.h.create(manager)

    def test_responsible_must_be_a_team_member_of_the_same_organization(self):
        owner = self.h.owner()
        with self.assertRaises(DomainError):
            self.h.create(owner, owner_id=999)

    def test_client_from_another_organization_is_not_found(self):
        owner = self.h.owner()
        with self.assertRaises(NotFound):
            self.h.create(owner, client_id=12345)


class InternalApprovalTests(TestCase):
    def setUp(self):
        self.h = Harness()
        self.owner = self.h.owner()
        self.creative = actor(Role.CREATIVE, 3, client_ids={Harness.CLIENT_ID})
        self.content_id = self.h.create(self.creative)
        self.h.service.move_to(self.creative, self.content_id, ContentState.PLANNED)
        self.h.service.move_to(self.creative, self.content_id, ContentState.IN_PRODUCTION)
        self.h.service.move_to(self.creative, self.content_id, ContentState.INTERNAL_REVIEW)

    def test_creative_cannot_approve_internally(self):
        with self.assertRaises(Forbidden):
            self.h.service.decide_internal(self.creative, self.content_id, approve=True)
        self.assertEqual(self.h.repository.rows[self.content_id].state, ContentState.INTERNAL_REVIEW)

    def test_owner_approval_moves_to_client_review_and_audits_it(self):
        self.h.service.decide_internal(self.owner, self.content_id, approve=True)

        self.assertEqual(self.h.repository.rows[self.content_id].state, ContentState.CLIENT_REVIEW)
        self.assertIn("content.approval_recorded", self.h.audit.actions())

    def test_rejected_piece_is_saved_with_its_comment(self):
        self.h.service.decide_internal(self.owner, self.content_id, approve=False, comment="Trocar a cor")

        content = self.h.repository.rows[self.content_id]
        self.assertEqual(content.state, ContentState.IN_PRODUCTION)
        self.assertEqual(content.approvals[-1].comment, "Trocar a cor")

    def test_failed_domain_rule_saves_nothing_and_audits_nothing(self):
        audit_before = len(self.h.audit.events)

        with self.assertRaises(DomainError):
            self.h.service.decide_internal(self.owner, self.content_id, approve=False, comment=" ")

        content = self.h.repository.rows[self.content_id]
        self.assertEqual(content.state, ContentState.INTERNAL_REVIEW)
        self.assertEqual(content.approvals, [])
        self.assertEqual(len(self.h.audit.events), audit_before)


class ClientApprovalTests(TestCase):
    def setUp(self):
        self.h = Harness()
        self.owner = self.h.owner()
        self.creative = actor(Role.CREATIVE, 3, client_ids={Harness.CLIENT_ID})
        self.content_id = self.h.create(self.creative)
        for target in (ContentState.PLANNED, ContentState.IN_PRODUCTION, ContentState.INTERNAL_REVIEW):
            self.h.service.move_to(self.creative, self.content_id, target)
        self.h.service.decide_internal(self.owner, self.content_id, approve=True)

        self.client_user = actor(Role.CLIENT, 20, client_ids={Harness.CLIENT_ID})

    def test_client_of_another_brand_cannot_see_the_piece(self):
        other_client = actor(Role.CLIENT, 21, client_ids={77})
        with self.assertRaises(NotFound):
            self.h.service.decide_client(other_client, self.content_id, approve=True)

    def test_client_approval_completes_the_review(self):
        self.h.service.decide_client(self.client_user, self.content_id, approve=True)
        self.assertEqual(self.h.repository.rows[self.content_id].state, ContentState.APPROVED)

    def test_client_cannot_schedule_even_after_approving(self):
        self.h.service.decide_client(self.client_user, self.content_id, approve=True)
        with self.assertRaises(Forbidden):
            self.h.service.schedule(self.client_user, self.content_id, when=NOW + timedelta(days=1))

    def test_client_cannot_move_content_by_hand(self):
        with self.assertRaises(Forbidden):
            self.h.service.move_to(self.client_user, self.content_id, ContentState.PLANNED)


class EditingAndSchedulingTests(TestCase):
    def setUp(self):
        self.h = Harness()
        self.owner = self.h.owner()
        self.creative = actor(Role.CREATIVE, 3, client_ids={Harness.CLIENT_ID})
        self.content_id = self.h.create(self.creative)
        for target in (ContentState.PLANNED, ContentState.IN_PRODUCTION, ContentState.INTERNAL_REVIEW):
            self.h.service.move_to(self.creative, self.content_id, target)
        self.h.service.decide_internal(self.owner, self.content_id, approve=True)
        self.h.service.decide_client(
            actor(Role.CLIENT, 20, client_ids={Harness.CLIENT_ID}), self.content_id, approve=True
        )

    def test_editing_an_approved_piece_is_audited_as_a_state_change(self):
        self.h.service.add_version(self.creative, self.content_id, VersionData(caption="Nova legenda"))

        self.assertEqual(self.h.repository.rows[self.content_id].state, ContentState.INTERNAL_REVIEW)
        states = [e["metadata"]["to"] for e in self.h.audit.events if e["action"] == "content.state_changed"]
        self.assertEqual(states[-1], "internal_review")

    def test_only_a_manager_or_owner_can_schedule(self):
        with self.assertRaises(Forbidden):
            self.h.service.schedule(self.creative, self.content_id, when=NOW + timedelta(days=1))

    def test_manager_schedules_and_the_clock_is_used_for_validation(self):
        manager = actor(Role.ACCOUNT_MANAGER, 4, client_ids={Harness.CLIENT_ID})

        with self.assertRaises(DomainError):
            self.h.service.schedule(manager, self.content_id, when=NOW)  # not in the future

        self.h.service.schedule(manager, self.content_id, when=NOW + timedelta(days=1))
        self.assertEqual(self.h.repository.rows[self.content_id].state, ContentState.SCHEDULED)

    def test_failure_then_retry_keeps_full_history(self):
        manager = actor(Role.ACCOUNT_MANAGER, 4, client_ids={Harness.CLIENT_ID})
        self.h.service.schedule(manager, self.content_id, when=NOW + timedelta(days=1))
        self.h.service.mark_failed(manager, self.content_id, reason="Rede fora do ar")
        self.h.service.schedule(manager, self.content_id, when=NOW + timedelta(days=2))

        content = self.h.repository.rows[self.content_id]
        self.assertEqual(content.state, ContentState.SCHEDULED)
        path = [e["metadata"]["to"] for e in self.h.audit.events if e["action"] == "content.state_changed"]
        self.assertIn("failed", path)


class FreelancerScopeTests(TestCase):
    def setUp(self):
        self.h = Harness()
        self.owner = self.h.owner()
        self.assigned = actor(Role.FREELANCER, 8, client_ids={Harness.CLIENT_ID})
        self.other_freelancer = actor(Role.FREELANCER, 9, client_ids={Harness.CLIENT_ID})
        self.h.repository.internal_members.update({(Harness.ORGANIZATION_ID, 8), (Harness.ORGANIZATION_ID, 9)})
        self.piece = self.h.create(self.owner, owner_id=8)

    def test_freelancer_can_edit_the_piece_assigned_to_them(self):
        self.h.service.add_version(self.assigned, self.piece, VersionData(caption="Minha versão"))
        self.assertEqual(self.h.repository.rows[self.piece].latest_version.number, 2)

    def test_freelancer_cannot_touch_a_piece_assigned_to_someone_else(self):
        with self.assertRaises(NotFound):
            self.h.service.add_version(self.other_freelancer, self.piece, VersionData(caption="Invasão"))
        self.assertEqual(self.h.repository.rows[self.piece].latest_version.number, 1)
