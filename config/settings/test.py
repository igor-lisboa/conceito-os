"""Settings used by the test suite.

By default tests run on SQLite in memory, so they need no database server.
To run the suite against the real MySQL engine (for example the Docker database
from docker-compose.yml), set TEST_DATABASE=mysql. Django then creates a separate
test_<MYSQL_DATABASE> database and drops it afterwards. Your data is not touched.
"""

import os

from .base import *  # noqa: F401,F403

SECRET_KEY = "test-only-secret-key"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]

if os.environ.get("TEST_DATABASE", "sqlite").lower() == "mysql":
    # Keep DATABASES from base.py: it reads the MYSQL_* variables.
    pass
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
