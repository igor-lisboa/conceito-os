"""Database settings, read from environment variables.

Two ways to configure the database:

1. PostgreSQL (production). Set DATABASE_URL_READWRITE (the primary, used for every write
   and for reads that must be current). Optionally set DATABASE_URL_READONLY: a second
   connection, alias "replica", used by the read router for lists, counts and reports
   (apps/core/db_router.py). Give the read-only string a role that can only SELECT.

2. MySQL (local Docker and tests). Used when DATABASE_URL_READWRITE is not set: MYSQL_*.

Connection tuning (both URLs):
- DB_CONN_MAX_AGE: seconds to keep a connection open. 0 suits serverless (Vercel); a
  long-running server can use 60 or more. Use an external pooler (PgBouncer or the
  provider's pooler) when many instances connect.
- DB_CONNECT_TIMEOUT: seconds to wait when connecting.
- DB_STATEMENT_TIMEOUT_MS: a query longer than this is stopped by the server.
Connections are checked before use (CONN_HEALTH_CHECKS), so a dropped one is replaced.
Defaults are PROPOSALS, to be checked with the load test (NFR-032).
"""

from urllib.parse import parse_qs, unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured

POSTGRES_SCHEMES = {"postgres", "postgresql"}


def _int(env, name, default):
    return int(env.get(name, default))


def _postgres(url, env):
    parts = urlsplit(url)
    if parts.scheme not in POSTGRES_SCHEMES:
        raise ImproperlyConfigured("The database URL must start with postgresql://")
    query = {key: values[-1] for key, values in parse_qs(parts.query).items()}
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parts.path.lstrip("/"),
        "USER": unquote(parts.username or ""),
        "PASSWORD": unquote(parts.password or ""),
        "HOST": parts.hostname or "",
        "PORT": str(parts.port or 5432),
        "CONN_MAX_AGE": _int(env, "DB_CONN_MAX_AGE", 0),
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "sslmode": query.get("sslmode", "require"),
            "connect_timeout": _int(env, "DB_CONNECT_TIMEOUT", 5),
            "options": f"-c statement_timeout={_int(env, 'DB_STATEMENT_TIMEOUT_MS', 15000)}",
        },
    }


def mysql_settings(env):
    return {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env.get("MYSQL_DATABASE", "conceito_os"),
            "USER": env.get("MYSQL_USER", ""),
            "PASSWORD": env.get("MYSQL_PASSWORD", ""),
            "HOST": env.get("MYSQL_HOST", "127.0.0.1"),
            "PORT": env.get("MYSQL_PORT", "3306"),
            "CONN_MAX_AGE": _int(env, "DB_CONN_MAX_AGE", 0),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }


def database_settings(env):
    """Return the Django DATABASES setting for the environment given."""
    primary_url = env.get("DATABASE_URL_READWRITE", "").strip()
    if not primary_url:
        return mysql_settings(env)

    databases = {"default": _postgres(primary_url, env)}
    replica_url = env.get("DATABASE_URL_READONLY", "").strip()
    if replica_url:
        replica = _postgres(replica_url, env)
        # Tests run against the same database as the primary, so the replica is a mirror.
        replica["TEST"] = {"MIRROR": "default"}
        databases["replica"] = replica
    return databases
