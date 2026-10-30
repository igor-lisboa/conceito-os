from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from accounts.middleware import ACTIVE_MEMBERSHIP_SESSION_KEY, get_active_membership
from accounts.models import Membership, Organization, Role

User = get_user_model()


class ActiveMembershipTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", password="x")
        self.agency_a = Organization.objects.create(name="Agência A")
        self.agency_b = Organization.objects.create(name="Agência B")
        self.membership_a = Membership.objects.create(user=self.user, organization=self.agency_a, role=Role.OWNER)
        self.membership_b = Membership.objects.create(user=self.user, organization=self.agency_b, role=Role.CREATIVE)

    def _request(self, session_membership_id=None):
        request = RequestFactory().get("/")
        request.user = self.user
        request.session = {}
        if session_membership_id is not None:
            request.session[ACTIVE_MEMBERSHIP_SESSION_KEY] = session_membership_id
        return request

    def test_defaults_to_first_membership_without_session_choice(self):
        self.assertEqual(get_active_membership(self._request()), self.membership_a)

    def test_uses_membership_chosen_in_session(self):
        request = self._request(session_membership_id=self.membership_b.id)
        self.assertEqual(get_active_membership(request), self.membership_b)

    def test_ignores_session_choice_that_belongs_to_another_user(self):
        other = User.objects.create_user("bruno", password="x")
        foreign = Membership.objects.create(
            user=other, organization=Organization.objects.create(name="Outra"), role=Role.OWNER
        )
        request = self._request(session_membership_id=foreign.id)
        self.assertEqual(get_active_membership(request), self.membership_a)

    def test_user_without_membership_gets_none(self):
        lonely = User.objects.create_user("carla", password="x")
        request = self._request()
        request.user = lonely
        self.assertIsNone(get_active_membership(request))
