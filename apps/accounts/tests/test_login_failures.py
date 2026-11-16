"""Sign-in failure counters live in the database and count atomically (SEC-008, TD-S9)."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts import throttle
from apps.accounts.models import LoginFailure


class LoginFailureCounterTests(TestCase):
    def count_for(self, kind, value):
        key = throttle._key(kind, value)
        return LoginFailure.objects.filter(key=key).values_list("count", flat=True).first()

    def test_each_failure_is_counted_once_for_account_and_address(self):
        for _ in range(3):
            throttle.record_failure("ana@conceito.com.br", "10.0.0.1")

        self.assertEqual(self.count_for("account", "ana@conceito.com.br"), 3)
        self.assertEqual(self.count_for("address", "10.0.0.1"), 3)

    def test_the_account_limit_locks_at_five_failures(self):
        for _ in range(4):
            throttle.record_failure("ana@conceito.com.br", "10.0.0.1")
        self.assertFalse(throttle.is_locked("ana@conceito.com.br", "10.0.0.1"))

        throttle.record_failure("ana@conceito.com.br", "10.0.0.1")
        self.assertTrue(throttle.is_locked("ana@conceito.com.br", "10.0.0.1"))

    def test_the_address_limit_locks_at_twenty_failures(self):
        for i in range(throttle.MAX_FAILURES_PER_ADDRESS):
            throttle.record_failure(f"pessoa{i}@conceito.com.br", "10.0.0.9")

        self.assertTrue(throttle.is_locked("nova@conceito.com.br", "10.0.0.9"))
        self.assertFalse(throttle.is_locked("nova@conceito.com.br", "10.0.0.8"))

    def test_clearing_removes_the_account_count_only(self):
        for _ in range(5):
            throttle.record_failure("ana@conceito.com.br", "10.0.0.1")

        throttle.clear_failures("ana@conceito.com.br")

        self.assertIsNone(self.count_for("account", "ana@conceito.com.br"))
        self.assertEqual(self.count_for("address", "10.0.0.1"), 5)

    def test_an_expired_count_starts_again(self):
        for _ in range(5):
            throttle.record_failure("ana@conceito.com.br", "10.0.0.1")
        self.assertTrue(throttle.is_locked("ana@conceito.com.br", "10.0.0.1"))

        LoginFailure.objects.update(expires_at=timezone.now() - timedelta(seconds=1))

        self.assertFalse(throttle.is_locked("ana@conceito.com.br", "10.0.0.1"))
        throttle.record_failure("ana@conceito.com.br", "10.0.0.1")
        self.assertEqual(self.count_for("account", "ana@conceito.com.br"), 1)

    def test_expired_rows_are_removed_on_the_next_failure(self):
        throttle.record_failure("antiga@conceito.com.br", "10.0.0.2")
        LoginFailure.objects.update(expires_at=timezone.now() - timedelta(seconds=1))

        throttle.record_failure("nova@conceito.com.br", "10.0.0.3")

        self.assertIsNone(self.count_for("account", "antiga@conceito.com.br"))
        self.assertEqual(self.count_for("account", "nova@conceito.com.br"), 1)
