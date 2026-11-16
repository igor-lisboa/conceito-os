"""Database settings come from the environment: PostgreSQL read/write and read-only, or MySQL."""

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.database import database_settings


class DatabaseSettingsTests(SimpleTestCase):
    def test_without_a_postgres_url_the_mysql_variables_are_used(self):
        databases = database_settings({"MYSQL_DATABASE": "x", "MYSQL_USER": "u"})
        self.assertEqual(databases["default"]["ENGINE"], "django.db.backends.mysql")
        self.assertNotIn("replica", databases)

    def test_the_read_write_url_becomes_the_primary(self):
        databases = database_settings({"DATABASE_URL_READWRITE": "postgresql://app:secret@db.example.com:6543/conceito"})
        primary = databases["default"]
        self.assertEqual(primary["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual((primary["HOST"], primary["PORT"], primary["NAME"]), ("db.example.com", "6543", "conceito"))
        self.assertEqual((primary["USER"], primary["PASSWORD"]), ("app", "secret"))
        self.assertTrue(primary["CONN_HEALTH_CHECKS"])

    def test_special_characters_in_the_password_are_decoded(self):
        databases = database_settings({"DATABASE_URL_READWRITE": "postgresql://app:p%40ss%23w@h/db"})
        self.assertEqual(databases["default"]["PASSWORD"], "p@ss#w")

    def test_ssl_is_required_by_default_and_can_be_set_in_the_url(self):
        default = database_settings({"DATABASE_URL_READWRITE": "postgresql://a:b@h/db"})["default"]
        local = database_settings({"DATABASE_URL_READWRITE": "postgresql://a:b@h/db?sslmode=disable"})["default"]
        self.assertEqual(default["OPTIONS"]["sslmode"], "require")
        self.assertEqual(local["OPTIONS"]["sslmode"], "disable")

    def test_the_read_only_url_becomes_the_replica_alias(self):
        databases = database_settings(
            {
                "DATABASE_URL_READWRITE": "postgresql://rw:a@primary/db",
                "DATABASE_URL_READONLY": "postgresql://ro:b@replica/db",
            }
        )
        self.assertEqual(databases["replica"]["USER"], "ro")
        self.assertEqual(databases["replica"]["HOST"], "replica")

    def test_tuning_comes_from_the_environment(self):
        databases = database_settings(
            {
                "DATABASE_URL_READWRITE": "postgresql://a:b@h/db",
                "DB_CONN_MAX_AGE": "60",
                "DB_CONNECT_TIMEOUT": "3",
                "DB_STATEMENT_TIMEOUT_MS": "9000",
            }
        )["default"]
        self.assertEqual(databases["CONN_MAX_AGE"], 60)
        self.assertEqual(databases["OPTIONS"]["connect_timeout"], 3)
        self.assertIn("statement_timeout=9000", databases["OPTIONS"]["options"])

    def test_a_non_postgres_url_is_refused(self):
        with self.assertRaises(ImproperlyConfigured):
            database_settings({"DATABASE_URL_READWRITE": "mysql://a:b@h/db"})
