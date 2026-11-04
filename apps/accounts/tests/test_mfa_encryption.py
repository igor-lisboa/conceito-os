"""The MFA secret is encrypted at rest (TD-S11, AUTH-004, SEC-005)."""

import importlib

from django.apps import apps as global_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase, override_settings

from apps.accounts import fields
from apps.accounts.models import MFADevice
from apps.core.testing import make_organization, make_owner

PLAIN = "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"
OTHER_KEY = "Yd3gZb0wE3sJ6KqS0VZ1Yx8o6uM3V7cR2m0y9Yq1bH8="


def db_pk(pk):
    return MFADevice._meta.pk.get_db_prep_value(pk, connection)


def raw_secret(device_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT secret FROM accounts_mfadevice WHERE id = %s", [db_pk(device_id)])
        return cursor.fetchone()[0]


class EncryptedSecretTests(TestCase):
    def setUp(self):
        self.owner = make_owner(make_organization())

    def test_the_database_holds_a_token_not_the_secret(self):
        device = MFADevice.objects.create(user=self.owner.user, secret=PLAIN)

        stored = raw_secret(device.pk)

        self.assertNotEqual(stored, PLAIN)
        self.assertNotIn(PLAIN, stored)
        self.assertTrue(stored.startswith(fields.TOKEN_PREFIX))

    def test_reading_the_device_gives_the_plain_secret_back(self):
        device = MFADevice.objects.create(user=self.owner.user, secret=PLAIN)

        self.assertEqual(MFADevice.objects.get(pk=device.pk).secret, PLAIN)

    def test_updating_the_secret_stores_it_encrypted_again(self):
        device = MFADevice.objects.create(user=self.owner.user, secret=PLAIN)
        MFADevice.objects.filter(pk=device.pk).update(secret="ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")

        self.assertEqual(MFADevice.objects.get(pk=device.pk).secret, "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")

    def test_a_wrong_key_refuses_to_return_a_secret(self):
        device = MFADevice.objects.create(user=self.owner.user, secret=PLAIN)

        with override_settings(MFA_ENCRYPTION_KEY=OTHER_KEY):
            fields._fernet_for.cache_clear()
            with self.assertRaises(ValueError):
                _ = MFADevice.objects.get(pk=device.pk).secret
        fields._fernet_for.cache_clear()

    def test_production_refuses_to_run_without_a_key(self):
        with override_settings(MFA_ENCRYPTION_KEY="", DEBUG=False):
            with self.assertRaises(ImproperlyConfigured):
                fields.encrypt_secret(PLAIN)

    def test_local_development_derives_a_key_so_the_app_runs(self):
        with override_settings(MFA_ENCRYPTION_KEY="", DEBUG=True):
            token = fields.encrypt_secret(PLAIN)
            self.assertEqual(fields.decrypt_secret(token), PLAIN)


class EncryptExistingMigrationTests(TestCase):
    """The data step of migration 0004 encrypts secrets stored in plain text before the change."""

    def setUp(self):
        self.owner = make_owner(make_organization())
        self.migration = importlib.import_module("apps.accounts.migrations.0004_encrypt_mfa_secret")

    def test_plain_secrets_are_encrypted_and_already_encrypted_ones_are_left_alone(self):
        device = MFADevice.objects.create(user=self.owner.user, secret=PLAIN)
        with connection.cursor() as cursor:
            cursor.execute("UPDATE accounts_mfadevice SET secret = %s WHERE id = %s", [PLAIN, db_pk(device.pk)])

        self.migration._encrypt_existing(global_apps, None)
        once = raw_secret(device.pk)
        self.migration._encrypt_existing(global_apps, None)

        self.assertTrue(once.startswith(fields.TOKEN_PREFIX))
        self.assertEqual(raw_secret(device.pk), once)
        self.assertEqual(MFADevice.objects.get(pk=device.pk).secret, PLAIN)

    def test_the_reverse_step_restores_plain_text(self):
        device = MFADevice.objects.create(user=self.owner.user, secret=PLAIN)

        self.migration._decrypt_existing(global_apps, None)

        self.assertEqual(raw_secret(device.pk), PLAIN)


class UpgradeMigrationTests(TransactionTestCase):
    """Running migration 0004 on a database that already has a plain-text secret."""

    migrate_from = [("accounts", "0003_user_email_language")]
    migrate_to = [("accounts", "0004_encrypt_mfa_secret")]

    def test_an_existing_plain_secret_is_encrypted_by_the_upgrade(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        User = old_apps.get_model("accounts", "User")
        MFADeviceOld = old_apps.get_model("accounts", "MFADevice")
        user = User.objects.create(username="ana", email="ana@example.com")
        MFADeviceOld.objects.create(user=user, secret=PLAIN, confirmed=True)

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.migrate_to)
        try:
            device = MFADevice.objects.get(user__email="ana@example.com")
            self.assertEqual(device.secret, PLAIN)
            self.assertNotEqual(raw_secret(device.pk), PLAIN)
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
