"""Each person chooses the language of their emails on their own account page (NTF-010)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.core.testing import make_membership, make_organization


class AccountLanguageTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.membership = make_membership(self.agency, Role.CLIENT)
        self.client.force_login(self.membership.user)

    def test_the_account_page_is_available_to_every_signed_in_role(self):
        response = self.client.get(reverse("account"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email language")

    def test_anonymous_people_are_sent_to_sign_in(self):
        self.client.logout()

        response = self.client.get(reverse("account"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_choosing_a_language_saves_it_on_the_person(self):
        response = self.client.post(reverse("account"), {"language": "en"})

        self.assertRedirects(response, reverse("account"))
        self.membership.user.refresh_from_db()
        self.assertEqual(self.membership.user.language, "en")

    def test_the_language_can_be_left_unchosen(self):
        self.membership.user.language = "en"
        self.membership.user.save()

        self.client.post(reverse("account"), {"language": ""})

        self.membership.user.refresh_from_db()
        self.assertEqual(self.membership.user.language, "")

    def test_an_unknown_language_is_rejected(self):
        response = self.client.post(reverse("account"), {"language": "fr"})

        self.assertEqual(response.status_code, 200)
        self.membership.user.refresh_from_db()
        self.assertEqual(self.membership.user.language, "")
