"""Production refuses to start without the MFA encryption key (TD-S11)."""

from django.test import SimpleTestCase, override_settings

from apps.accounts import checks


class MFAKeyCheckTests(SimpleTestCase):
    def test_production_without_a_key_is_an_error(self):
        with override_settings(DEBUG=False, MFA_ENCRYPTION_KEY=""):
            errors = checks.check_mfa_encryption_key(None)
        self.assertEqual([error.id for error in errors], ["accounts.E001"])

    def test_production_with_a_key_passes(self):
        with override_settings(DEBUG=False, MFA_ENCRYPTION_KEY="x"):
            self.assertEqual(checks.check_mfa_encryption_key(None), [])

    def test_local_development_does_not_need_a_key(self):
        with override_settings(DEBUG=True, MFA_ENCRYPTION_KEY=""):
            self.assertEqual(checks.check_mfa_encryption_key(None), [])
