"""Sign-in attempt limits (SEC-008), per-organization time zone (CAL-011), and settings."""

from django.core.cache import cache
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.middleware import OrganizationTimezoneMiddleware
from accounts.roles import Role
from core.testing import make_membership, make_organization, make_owner


class SignInAttemptLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.owner.user.set_password("Senha-Certa-2026!")
        self.owner.user.save()

    def fail(self, email="", password="errada"):
        return self.client.post(reverse("login"), {"username": email or self.owner.user.email, "password": password})

    def test_the_sixth_wrong_password_is_refused_even_with_the_right_one(self):
        for _ in range(5):
            self.fail()

        response = self.fail(password="Senha-Certa-2026!")

        self.assertEqual(response.status_code, 429)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_a_successful_sign_in_clears_the_count(self):
        for _ in range(4):
            self.fail()
        self.client.post(reverse("login"), {"username": self.owner.user.email, "password": "Senha-Certa-2026!"})
        self.client.logout()

        for _ in range(4):
            self.fail()
        response = self.fail(password="Senha-Certa-2026!")

        self.assertNotEqual(response.status_code, 429)

    def test_the_limit_is_per_account_not_global(self):
        other = make_owner(make_organization("Outra"))
        other.user.set_password("Outra-Senha-2026!")
        other.user.save()
        for _ in range(5):
            self.fail()

        response = self.client.post(
            reverse("login"), {"username": other.user.email, "password": "Outra-Senha-2026!"}
        )
        self.assertNotEqual(response.status_code, 429)

    def test_the_limit_message_is_shown(self):
        for _ in range(5):
            self.fail()
        response = self.fail()
        self.assertContains(response, "Too many failed attempts", status_code=429)


class OrganizationTimezoneTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.factory = RequestFactory()

    def seen_zone(self, membership):
        seen = {}

        def view(request):
            seen["zone"] = timezone.get_current_timezone_name()
            return None

        request = self.factory.get("/")
        request.membership = membership
        OrganizationTimezoneMiddleware(view)(request)
        return seen["zone"]

    def test_pages_use_the_organization_time_zone(self):
        self.agency.timezone = "America/Manaus"
        self.agency.save()
        self.assertEqual(self.seen_zone(self.owner), "America/Manaus")

    def test_a_wrong_time_zone_falls_back_to_utc(self):
        self.agency.timezone = "Not/AZone"
        self.agency.save()
        self.assertEqual(self.seen_zone(self.owner), "UTC")

    def test_no_membership_uses_utc(self):
        self.assertEqual(self.seen_zone(None), "UTC")



class OrganizationSettingsTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)

    def test_owner_changes_name_and_time_zone(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("organization_settings"),
            {"name": "Conceito Co", "timezone": "America/Fortaleza"},
        )
        self.agency.refresh_from_db()
        self.assertEqual(self.agency.timezone, "America/Fortaleza")

    def test_time_zone_must_come_from_the_list(self):
        self.client.force_login(self.owner.user)
        response = self.client.post(reverse("organization_settings"), {"name": "X", "timezone": "Mars/Olympus"})
        self.assertEqual(response.status_code, 200)
        self.agency.refresh_from_db()
        self.assertNotEqual(self.agency.timezone, "Mars/Olympus")

    def test_account_manager_cannot_open_settings(self):
        manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        self.client.force_login(manager.user)
        self.assertEqual(self.client.get(reverse("organization_settings")).status_code, 403)
