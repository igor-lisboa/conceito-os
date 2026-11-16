"""People are signed out after a period without activity (TD-S8, answer 6A)."""

from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.core.testing import make_organization, make_owner


@override_settings(SESSION_IDLE_TIMEOUT_SECONDS=600)
class IdleTimeoutTests(TestCase):
    def setUp(self):
        self.owner = make_owner(make_organization())
        self.client.force_login(self.owner.user)

    def test_an_active_person_stays_signed_in(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_a_person_idle_too_long_is_signed_out(self):
        session = self.client.session
        session["last_activity"] = (timezone.now() - timedelta(seconds=601)).timestamp()
        session.save()

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("timeout=1", response["Location"])
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_activity_refreshes_the_timer(self):
        session = self.client.session
        session["last_activity"] = (timezone.now() - timedelta(seconds=500)).timestamp()
        session.save()

        self.client.get(reverse("home"))
        session = self.client.session
        self.assertGreater(session["last_activity"], (timezone.now() - timedelta(seconds=5)).timestamp())
