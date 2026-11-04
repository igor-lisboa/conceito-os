"""Sessions end when access is removed or the password changes (AUTH-003, AUTH-012)."""

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts import team
from apps.accounts.roles import Role
from apps.accounts.sessions import end_user_sessions
from apps.core.testing import make_membership, make_organization, make_owner


class SessionRevocationTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.member = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")

    def test_a_removed_member_with_an_open_session_is_signed_out(self):
        self.client.force_login(self.member.user)
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

        team.remove_member(self.owner, self.member)

        response = self.client.get(reverse("home"))
        login = f"{reverse(settings.LOGIN_URL)}?next={reverse('home')}"
        self.assertRedirects(response, login, fetch_redirect_response=False)

    def test_removing_access_leaves_other_people_signed_in(self):
        bruno = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="bruno")
        staying = Client()
        staying.force_login(bruno.user)

        team.remove_member(self.owner, self.member)

        self.assertEqual(staying.get(reverse("home")).status_code, 200)

    def test_end_user_sessions_counts_and_ends_only_that_user(self):
        bruno = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="bruno")
        first, second, other = Client(), Client(), Client()
        first.force_login(self.member.user)
        second.force_login(self.member.user)
        other.force_login(bruno.user)

        self.assertEqual(end_user_sessions(self.member.user), 2)
        self.assertNotEqual(first.get(reverse("home")).status_code, 200)
        self.assertEqual(other.get(reverse("home")).status_code, 200)

    def test_changing_the_password_signs_out_other_sessions(self):
        other = Client()
        self.client.force_login(self.member.user)
        other.force_login(self.member.user)
        self.member.user.set_password("nova-senha-forte-2026")
        self.member.user.save()

        response = other.get(reverse("home"))

        self.assertNotEqual(response.status_code, 200)
