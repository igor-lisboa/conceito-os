"""Settings used by the test suite.

By default tests run on SQLite in memory, so they need no database server.
To run the suite against PostgreSQL (the production engine, local Docker container from
docker-compose.yml), set TEST_DATABASE=postgres. Django then creates a separate test
database and drops it afterwards. Your data is not touched. The test settings never use
the production URL from .env.
"""

import os

from .base import *  # noqa: F401,F403

SECRET_KEY = "test-only-secret-key"
# Test-only key for the MFA secrets. Never used outside the test suite.
MFA_ENCRYPTION_KEY = "1OdtVyP4W-5XAoFCefzo8FN2CMQoYg6Bos_BB8uqT_E="
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]

# The test database is always a local one, never the production URL from .env.
TEST_DATABASE_MODE = os.environ.get("TEST_DATABASE", "sqlite").lower()
if TEST_DATABASE_MODE == "postgres":
    # Local Docker Postgres (docker-compose.yml). Tests create and drop a test_ database on it.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "conceito_os"),
            "USER": os.environ.get("POSTGRES_USER", "conceito"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "conceito-local-only"),
            "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "OPTIONS": {"sslmode": "disable"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "tests"},
}

# Faster password hashing keeps the test suite quick.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
