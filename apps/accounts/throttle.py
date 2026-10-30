"""Limit failed sign-in attempts, per account and per network address.

Counts live in Django's cache. Locally that is the database cache (createcachetable);
on Vercel each instance has its own memory, so the limit is per instance until a shared
cache is chosen (see docs/technical-debt.md, TD-12). The per-account limit still holds.
"""

import hashlib

from django.core.cache import cache

MAX_FAILURES = 5  # per account
MAX_FAILURES_PER_ADDRESS = 20
WINDOW_SECONDS = 15 * 60


def _key(kind, value):
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"login-failures:{kind}:{digest}"


def is_locked(identifier, address):
    failures_for_account = cache.get(_key("account", identifier), 0)
    failures_from_address = cache.get(_key("address", address), 0)
    return failures_for_account >= MAX_FAILURES or failures_from_address >= MAX_FAILURES_PER_ADDRESS


def record_failure(identifier, address):
    for kind, value in (("account", identifier), ("address", address)):
        key = _key(kind, value)
        # add() creates the counter if missing; incr() counts up within the window.
        if not cache.add(key, 1, timeout=WINDOW_SECONDS):
            cache.incr(key)


def clear_failures(identifier):
    cache.delete(_key("account", identifier))
