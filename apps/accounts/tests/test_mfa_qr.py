"""The MFA setup screen shows a QR code, with the typed key kept as a fallback (TD-S12, AUTH-004)."""

import time

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.accounts import mfa
from apps.accounts.models import MFADevice
from apps.core.testing import make_organization, make_owner

from .test_mfa import rfc6238_code


class MFAQRCodeTests(TestCase):
    def setUp(self):
        cache.clear()
        self.owner = make_owner(make_organization())
        self.client.force_login(self.owner.user)

    def test_pending_setup_shows_an_svg_qr_code_and_the_typed_key(self):
        response = self.client.get(reverse("mfa_setup"))

        device = MFADevice.objects.get(user=self.owner.user)
        self.assertContains(response, 'class="mfa-qr"')
        self.assertContains(response, "<svg")
        self.assertContains(response, device.secret)

    def test_the_svg_is_built_from_the_provisioning_link(self):
        svg = mfa.provisioning_svg("otpauth://totp/Conceito%20OS:ana@example.com?secret=ABC")

        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)

    def test_a_different_secret_gives_a_different_qr_code(self):
        first = mfa.provisioning_svg(mfa.provisioning_uri(mfa.new_secret(), "a@example.com"))
        second = mfa.provisioning_svg(mfa.provisioning_uri(mfa.new_secret(), "a@example.com"))

        self.assertNotEqual(first, second)

    def test_a_confirmed_device_shows_no_qr_code(self):
        self.client.get(reverse("mfa_setup"))
        device = MFADevice.objects.get(user=self.owner.user)
        self.client.post(reverse("mfa_setup"), {"code": rfc6238_code(device.secret, time.time())})

        response = self.client.get(reverse("mfa_setup"))

        self.assertNotContains(response, 'class="mfa-qr"')
        self.assertNotContains(response, "<svg")
