"""Base settings shared by every environment.

Everything that changes between machines comes from environment variables, so
the same code runs locally, in tests and on Vercel. See README.md for the list.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_local_env_file(path):
    """Read KEY=VALUE lines from a local .env file into os.environ.

    Variables already set in the shell win over the file. The file is git-ignored
    and does not exist on Vercel, where the variables come from the project settings.
    """
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_local_env_file(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# --- Core security ---------------------------------------------------------

# No default on purpose: if the variable is missing, Django refuses to start
# instead of running with a known key.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
DEBUG = env_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # Vercel terminates TLS
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 3600
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- Applications ----------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "clients",
    "production",
    "portal",
    "notifications",
    "crm",
    "reports",
    "tasks",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # picks the language per request
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "accounts.middleware.ActiveMembershipMiddleware",
    "accounts.middleware.OrganizationTimezoneMiddleware",
    "accounts.middleware.MFAEnforcementMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "notifications.context_processors.unread_notifications",
            ],
        },
    },
]

# --- Database (MySQL) ------------------------------------------------------
# The database is not provisioned yet. These settings are ready; run
# `python manage.py migrate` once the MySQL server exists (see README.md).

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE", "conceito_os"),
        "USER": os.environ.get("MYSQL_USER", ""),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
        "HOST": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.environ.get("MYSQL_PORT", "3306"),
        "CONN_MAX_AGE": int(os.environ.get("DJANGO_CONN_MAX_AGE", "0")),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Shared counters (sign-in attempt limits). The database cache is shared by every
# process. Create its table once: python manage.py createcachetable
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

# --- Auth ------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

# --- Internationalization --------------------------------------------------
# Product UI is Brazilian Portuguese. Stored times are UTC; the UI converts
# them to the organization's timezone.

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("pt-br", "Português (Brasil)"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static files ----------------------------------------------------------
# WhiteNoise serves static files straight from the app folders, so the site
# works on Vercel without a separate collectstatic step.

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
WHITENOISE_USE_FINDERS = True
# STATIC_ROOT is intentionally not set: nothing runs collectstatic (see docs/deployment.md).

# Uploaded files are not stored here yet: Vercel's filesystem is read-only
# and temporary. Media is a URL field until a storage decision is made.

# --- Email (SMTP) -----------------------------------------------------------
# Locally the defaults point to the Mailpit container (see docker-compose.yml).
# In production set these to the real SMTP provider (see docs/deployment.md).
# Tests never send real mail: Django's test runner uses an in-memory outbox.

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "127.0.0.1")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "1025"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", default=False)
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Conceito OS <no-reply@conceito.com.br>")

# Public address of the site, used to build links inside emails.
SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:8080").rstrip("/")

# How long a password reset link stays valid, in seconds (one day).
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24

# Shown in the client portal's contact page.
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "contato@conceito.com.br")

# --- Logging ------------------------------------------------------------------
# Everything goes to standard output: Vercel and Docker both collect it.
# Failed emails, failed notifications and server errors are logged here (TD-14).

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "plain"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "accounts": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "notifications": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
    },
}
