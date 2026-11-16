"""Read/write routing between the primary database and the optional read-only replica.

Rules (performance with correctness):
- Every write goes to the primary ("default"). The replica is never written to.
- Reads of lists, counts and reports (REPLICA_APPS) go to the replica when one is configured.
- Reads that must be current are always on the primary:
  * sessions, sign-in, team membership, MFA and notifications (access must change at once,
    AUTH-012, and a stale session would break sign-in);
  * any read inside a transaction (a read-modify-write on a stale copy could lose a change);
  * the rest of a request that changed data, and for a few seconds after it (see
    PrimaryAfterWriteMiddleware), so a person never sees their own change missing.
"""

import time
from contextlib import contextmanager
from contextvars import ContextVar

from django.conf import settings
from django.db import connections

PRIMARY = "default"
REPLICA = "replica"
# Apps whose reads may lag a little behind the primary. Keep this list short and deliberate.
REPLICA_APPS = {"production", "clients", "reports", "tasks", "crm", "core"}
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
STICKY_SESSION_KEY = "primary_until"

_force_primary = ContextVar("force_primary", default=False)


def replica_configured():
    return REPLICA in settings.DATABASES


@contextmanager
def primary_only():
    """Read from the primary for everything inside this block."""
    token = _force_primary.set(True)
    try:
        yield
    finally:
        _force_primary.reset(token)


class ReplicaRouter:
    def db_for_read(self, model, **hints):
        if not replica_configured() or _force_primary.get():
            return PRIMARY
        if connections[PRIMARY].in_atomic_block:
            return PRIMARY
        if model._meta.app_label in REPLICA_APPS:
            return REPLICA
        return PRIMARY

    def db_for_write(self, model, **hints):
        return PRIMARY

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, **hints):
        # Migrations only ever run on the primary.
        return db == PRIMARY


class PrimaryAfterWriteMiddleware:
    """A request that changes data, and the requests of the same person for a few seconds
    after it, read from the primary. The window covers replication lag (PROPOSAL: 5 seconds)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not replica_configured():
            return self.get_response(request)

        sticky = self._sticky(request)
        is_write = request.method not in SAFE_METHODS
        if not (sticky or is_write):
            return self.get_response(request)

        with primary_only():
            response = self.get_response(request)

        if is_write and self._signed_in(request):
            window = getattr(settings, "DB_PRIMARY_STICKY_SECONDS", 5)
            request.session[STICKY_SESSION_KEY] = time.time() + window
        return response

    @staticmethod
    def _signed_in(request):
        user = getattr(request, "user", None)
        return user is not None and user.is_authenticated and hasattr(request, "session")

    def _sticky(self, request):
        if not self._signed_in(request):
            return False
        until = request.session.get(STICKY_SESSION_KEY)
        return until is not None and time.time() < until
