"""Which content events tell the team something (the recipients are tested in notifications/tests)."""

from datetime import timedelta
from unittest import TestCase

from apps.accounts.roles import Role
from apps.production.domain.states import ContentState

from .fakes import NOW, Harness, actor


class ContentNotificationEventsTests(TestCase):
    def setUp(self):
        self.h = Harness()
        self.owner = self.h.owner()
        self.creative = actor(Role.CREATIVE, 3, client_ids={Harness.CLIENT_ID})
        self.content_id = self.h.create(self.creative)
        self.client_user = actor(Role.CLIENT, 20, client_ids={Harness.CLIENT_ID})

    def test_moving_a_draft_around_sends_nothing(self):
        self.h.service.move_to(self.creative, self.content_id, ContentState.PLANNED)
        self.h.service.move_to(self.creative, self.content_id, ContentState.IN_PRODUCTION)
        self.assertEqual(self.h.notifier.calls, [])

    def test_sending_to_internal_review_notifies_the_managers(self):
        self._move_to_production()
        self.h.service.move_to(self.creative, self.content_id, ContentState.INTERNAL_REVIEW)
        self.assertEqual(self.h.notifier.kinds(), ["internal_review"])

    def test_internal_approval_asks_the_client_to_approve(self):
        self._move_to_internal_review()
        self.h.notifier.calls.clear()
        self.h.service.decide_internal(self.owner, self.content_id, approve=True)
        self.assertEqual(self.h.notifier.kinds(), ["client_review"])
        self.assertEqual(self.h.notifier.calls[-1]["client_id"], Harness.CLIENT_ID)
        self.assertEqual(self.h.notifier.calls[-1]["title"], "Post")

    def test_client_requesting_changes_notifies_the_team(self):
        self._move_to_client_review()
        self.h.notifier.calls.clear()
        self.h.service.decide_client(self.client_user, self.content_id, approve=False, comment="Mais leve")
        self.assertEqual(self.h.notifier.kinds(), ["changes_requested"])

    def test_client_approval_notifies_the_team(self):
        self._move_to_client_review()
        self.h.notifier.calls.clear()
        self.h.service.decide_client(self.client_user, self.content_id, approve=True)
        self.assertEqual(self.h.notifier.kinds(), ["approved_by_client"])

    def test_internal_rejection_goes_back_to_the_maker(self):
        self._move_to_internal_review()
        self.h.notifier.calls.clear()
        self.h.service.decide_internal(self.owner, self.content_id, approve=False, comment="Trocar a cor")
        self.assertEqual(self.h.notifier.kinds(), ["internal_rejected"])

    def test_publish_failure_carries_the_reason(self):
        self._move_to_client_review()
        self.h.service.decide_client(self.client_user, self.content_id, approve=True)
        self.h.notifier.calls.clear()
        self.h.service.schedule(self.owner, self.content_id, when=NOW + timedelta(days=1))
        self.h.service.mark_failed(self.owner, self.content_id, reason="Token expirado")

        self.assertEqual(self.h.notifier.kinds(), ["publish_failed"])
        self.assertEqual(self.h.notifier.calls[-1]["extra"], {"reason": "Token expirado"})

    def test_each_decision_gets_its_own_event_key(self):
        self._move_to_client_review()
        self.h.notifier.calls.clear()
        self.h.service.decide_client(self.client_user, self.content_id, approve=False, comment="Um")
        self.h.service.add_version(self.creative, self.content_id, _version("Ajustada"))
        self.h.service.move_to(self.creative, self.content_id, ContentState.IN_PRODUCTION)
        self.h.service.move_to(self.creative, self.content_id, ContentState.INTERNAL_REVIEW)
        self.h.service.decide_internal(self.owner, self.content_id, approve=True)
        self.h.service.decide_client(self.client_user, self.content_id, approve=False, comment="Dois")

        keys = [call["event_key"] for call in self.h.notifier.calls]
        self.assertEqual(len(keys), len(set(keys)))

    def test_without_a_notifier_the_service_still_works(self):
        self.h.service.notifier = None
        self.h.service.move_to(self.creative, self.content_id, ContentState.PLANNED)
        self.assertEqual(self.h.repository.rows[self.content_id].state, ContentState.PLANNED)

    # helpers ---------------------------------------------------------------

    def _move_to_production(self):
        self.h.service.move_to(self.creative, self.content_id, ContentState.PLANNED)
        self.h.service.move_to(self.creative, self.content_id, ContentState.IN_PRODUCTION)

    def _move_to_internal_review(self):
        self._move_to_production()
        self.h.service.move_to(self.creative, self.content_id, ContentState.INTERNAL_REVIEW)

    def _move_to_client_review(self):
        self._move_to_internal_review()
        self.h.service.decide_internal(self.owner, self.content_id, approve=True)


def _version(caption):
    from apps.production.domain.content import VersionData

    return VersionData(caption=caption)
