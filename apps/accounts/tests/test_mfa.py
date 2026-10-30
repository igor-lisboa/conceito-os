"""Two-step sign-in with an authenticator app (AUTH-004)."""

import base64
import hashlib
import hmac
import struct
import time

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.accounts import mfa
from apps.accounts.models import MFADevice
from apps.core.testing import make_organization, make_owner


def rfc6238_code(secret, when):
    """Independent reference implementation, from RFC 6238, to check ours against."""
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    counter = int(when // 30)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(value % 10**6).zfill(6)


class TotpTests(TestCase):
    def test_our_codes_match_the_rfc_reference_at_several_times(self):
        secret = mfa.new_secret()
        for when in (59, 1111111109, 1234567890, 2000000000):
            self.assertEqual(mfa._code_at(secret, int(when // 30)), rfc6238_code(secret, when))

    def test_a_correct_code_is_accepted_and_a_wrong_one_is_not(self):
        secret = mfa.new_secret()
        now = time.time()
        self.assertTrue(mfa.verify(secret, rfc6238_code(secret, now), now=now))
        self.assertFalse(mfa.verify(secret, "000000" if rfc6238_code(secret, now) != "000000" else "111111", now=now))

    def test_one_step_of_clock_drift_is_tolerated(self):
        secret = mfa.new_secret()
        now = time.time()
        previous_step = rfc6238_code(secret, now - 30)
        self.assertTrue(mfa.verify(secret, previous_step, now=now))

    def test_a_code_from_two_steps_ago_is_refused(self):
        secret = mfa.new_secret()
        now = time.time()
        self.assertFalse(mfa.verify(secret, rfc6238_code(secret, now - 90), now=now))

    def test_malformed_codes_are_refused(self):
        secret = mfa.new_secret()
        for bad in ("", "12345", "1234567", "abcdef", None):
            self.assertFalse(mfa.verify(secret, bad))

    def test_provisioning_link_carries_the_secret_and_issuer(self):
        uri = mfa.provisioning_uri("ABC123", "ana@conceito.com.br")
        self.assertTrue(uri.startswith("otpauth://totp/"))
        self.assertIn("secret=ABC123", uri)
        self.assertIn("issuer=Conceito%20OS", uri)


class MFAFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.owner.user.set_password("Senha-Forte-2026!")
        self.owner.user.save()

    def enable(self):
        self.client.force_login(self.owner.user)
        self.client.get(reverse("mfa_setup"))
        device = MFADevice.objects.get(user=self.owner.user)
        code = rfc6238_code(device.secret, time.time())
        self.client.post(reverse("mfa_setup"), {"code": code})
        device.refresh_from_db()
        return device

    def test_setup_shows_a_secret_and_turning_it_on_needs_a_correct_code(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("mfa_setup"))
        self.assertContains(response, "otpauth://totp/")

        self.client.post(reverse("mfa_setup"), {"code": "000000"})
        self.assertFalse(MFADevice.objects.get(user=self.owner.user).confirmed)

    def test_once_turned_on_the_next_sign_in_asks_for_a_code(self):
        self.enable()
        self.client.logout()
        self.client.login(username=self.owner.user.email, password="Senha-Forte-2026!")

        response = self.client.get(reverse("home"))

        self.assertRedirects(response, reverse("mfa_verify") + "?next=/", fetch_redirect_response=False)

    def test_entering_the_right_code_opens_the_session(self):
        device = self.enable()
        self.client.logout()
        self.client.login(username=self.owner.user.email, password="Senha-Forte-2026!")

        self.client.post(reverse("mfa_verify"), {"code": rfc6238_code(device.secret, time.time())})

        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_a_wrong_code_does_not_open_the_session(self):
        self.enable()
        self.client.logout()
        self.client.login(username=self.owner.user.email, password="Senha-Forte-2026!")

        self.client.post(reverse("mfa_verify"), {"code": "000000"})

        self.assertEqual(self.client.get(reverse("home")).status_code, 302)

    def test_repeated_wrong_codes_lock_the_verification(self):
        self.enable()
        self.client.logout()
        self.client.login(username=self.owner.user.email, password="Senha-Forte-2026!")
        for _ in range(5):
            self.client.post(reverse("mfa_verify"), {"code": "000000"})

        response = self.client.post(reverse("mfa_verify"), {"code": "000000"})

        self.assertEqual(response.status_code, 429)

    def test_accounts_without_mfa_are_not_asked(self):
        self.client.login(username=self.owner.user.email, password="Senha-Forte-2026!")
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_the_next_parameter_must_stay_on_this_site(self):
        device = self.enable()
        self.client.logout()
        self.client.login(username=self.owner.user.email, password="Senha-Forte-2026!")

        response = self.client.post(
            reverse("mfa_verify") + "?next=https://evil.example.com/",
            {"code": rfc6238_code(device.secret, time.time())},
        )

        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)
