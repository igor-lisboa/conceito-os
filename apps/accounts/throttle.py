"""Limit failed sign-in attempts, per account and per network address (SEC-008).

Counts are rows in the LoginFailure table, which every serverless instance shares. Each
failure is one atomic SQL UPDATE (count = count + 1), so parallel attempts are all
counted (closes TD-S9). A count lasts WINDOW_SECONDS from its first failure.
"""

import hashlib
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from .models import LoginFailure

MAX_FAILURES = 5  # per account
MAX_FAILURES_PER_ADDRESS = 20
WINDOW_SECONDS = 15 * 60


def _key(kind, value):
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"{kind}:{digest}"


def _live(now):
    return LoginFailure.objects.filter(expires_at__gt=now)


def _count(key, now):
    return _live(now).filter(key=key).values_list("count", flat=True).first() or 0


def is_locked(identifier, address):
    now = timezone.now()
    failures_for_account = _count(_key("account", identifier), now)
    failures_from_address = _count(_key("address", address), now)
    return failures_for_account >= MAX_FAILURES or failures_from_address >= MAX_FAILURES_PER_ADDRESS


def _bump(key, now):
    # 1. A live count: one atomic increment.
    if _live(now).filter(key=key).update(count=F("count") + 1):
        return
    expires_at = now + timedelta(seconds=WINDOW_SECONDS)
    # 2. An expired count: start a new window. Only one parallel request matches this
    #    filter; the others find a live count in step 1 next time, or fall to step 3.
    if LoginFailure.objects.filter(key=key, expires_at__lte=now).update(count=1, expires_at=expires_at):
        return
    # 3. No count yet: create it. A parallel request may have created it first.
    try:
        with transaction.atomic():
            LoginFailure.objects.create(key=key, count=1, expires_at=expires_at)
    except IntegrityError:
        _live(now).filter(key=key).update(count=F("count") + 1)


def record_failure(identifier, address):
    now = timezone.now()
    LoginFailure.objects.filter(expires_at__lte=now).delete()
    for kind, value in (("account", identifier), ("address", address)):
        _bump(_key(kind, value), now)


def clear_failures(identifier):
    LoginFailure.objects.filter(key=_key("account", identifier)).delete()
