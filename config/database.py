"""Database settings, read from environment variables. The engine is PostgreSQL.

- Production: DATABASE_URL_READWRITE is the primary (every write, and reads that must be
  current). DATABASE_URL_READONLY is optional: a second connection, alias "replica", for
  lists, counts and reports (apps/core/db_routing.py). Give it a role with SELECT rights only.
- Local development and tests: when DATABASE_URL_READWRITE is not set, the local Docker
  PostgreSQL from docker-compose.yml is used, configured with POSTGRES_* (defaults match it).

Connection tuning (both URLs):
- DB_CONN_MAX_AGE: seconds to keep a connection open. 0 suits serverless (Vercel); a
  long-running server can use 60 or more. Use the provider's pooler (PgBouncer or
  equivalent) when many instances connect.
- DB_CONNECT_TIMEOUT: seconds to wait when connecting.
- DB_STATEMENT_TIMEOUT_MS: a query longer than this is stopped by the server.
Connections are checked before use (CONN_HEALTH_CHECKS), so a dropped one is replaced.
The defaults are PROPOSALS, to be checked with the load test (NFR-032).
"""

from urllib.parse import parse_qs, unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured

POSTGRES_SCHEMES = {"postgres", "postgresql"}


def _int(env, name, default):
    return int(env.get(name, default))


def _connection(*, name, user, password, host, port, sslmode, env):
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": str(port),
        "CONN_MAX_AGE": _int(env, "DB_CONN_MAX_AGE", 0),
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {
            "sslmode": sslmode,
            "connect_timeout": _int(env, "DB_CONNECT_TIMEOUT", 5),
            "options": f"-c statement_timeout={_int(env, 'DB_STATEMENT_TIMEOUT_MS', 15000)}",
        },
    }


def _from_url(url, env):
    parts = urlsplit(url)
    if parts.scheme not in POSTGRES_SCHEMES:
        raise ImproperlyConfigured("The database URL must start with postgresql://")
    query = {key: values[-1] for key, values in parse_qs(parts.query).items()}
    return _connection(
        name=parts.path.lstrip("/"),
        user=unquote(parts.username or ""),
        password=unquote(parts.password or ""),
        host=parts.hostname or "",
        port=parts.port or 5432,
        sslmode=query.get("sslmode", "require"),
        env=env,
    )


def _local(env):
    """The local Docker PostgreSQL (docker-compose.yml). No TLS on localhost."""
    return _connection(
        name=env.get("POSTGRES_DB", "conceito_os"),
        user=env.get("POSTGRES_USER", "conceito"),
        password=env.get("POSTGRES_PASSWORD", "conceito-local-only"),
        host=env.get("POSTGRES_HOST", "127.0.0.1"),
        port=env.get("POSTGRES_PORT", "5432"),
        sslmode="disable",
        env=env,
    )


def database_settings(env):
    """Return the Django DATABASES setting for the environment given."""
    primary_url = env.get("DATABASE_URL_READWRITE", "").strip()
    databases = {"default": _from_url(primary_url, env) if primary_url else _local(env)}

    replica_url = env.get("DATABASE_URL_READONLY", "").strip()
    if replica_url:
        replica = _from_url(replica_url, env)
        # Tests run against the same database as the primary, so the replica is a mirror.
        replica["TEST"] = {"MIRROR": "default"}
        databases["replica"] = replica
    return databases
