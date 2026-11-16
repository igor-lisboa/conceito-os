"""The Vercel build migrates production only, and can be switched off (deployment guide)."""

from django.test import SimpleTestCase

import vercel_build


class ShouldMigrateTests(SimpleTestCase):
    def test_a_production_build_migrates(self):
        self.assertTrue(vercel_build.should_migrate({"VERCEL_ENV": "production"}))

    def test_a_preview_build_never_touches_the_database(self):
        self.assertFalse(vercel_build.should_migrate({"VERCEL_ENV": "preview"}))

    def test_a_local_build_does_not_migrate(self):
        self.assertFalse(vercel_build.should_migrate({}))

    def test_the_switch_turns_production_migrations_off(self):
        self.assertFalse(vercel_build.should_migrate({"VERCEL_ENV": "production", "RUN_MIGRATIONS": "0"}))

    def test_the_switch_on_keeps_them_on(self):
        self.assertTrue(vercel_build.should_migrate({"VERCEL_ENV": "production", "RUN_MIGRATIONS": "1"}))
