"""Reads go to the replica only when it is safe; writes always go to the primary (performance and correctness)."""

import time
from unittest.mock import patch

from django.conf import settings
from django.test import RequestFactory, TestCase, TransactionTestCase
from django.urls import reverse

from apps.accounts.models import Membership
from apps.core.db_routing import PRIMARY, REPLICA, PrimaryAfterWriteMiddleware, ReplicaRouter, primary_only
from apps.core.testing import make_organization, make_owner
from apps.production.models import ContentItem

REPLICA_CONFIG = dict(settings.DATABASES[PRIMARY], NAME=settings.DATABASES[PRIMARY]["NAME"])


class RouterWithoutReplicaTests(TestCase):
    def test_everything_uses_the_primary_when_no_replica_is_configured(self):
        router = ReplicaRouter()
        self.assertEqual(router.db_for_read(ContentItem), PRIMARY)
        self.assertEqual(router.db_for_write(ContentItem), PRIMARY)


class RouterWithReplicaTests(TransactionTestCase):
    def setUp(self):
        self.patch = patch.dict(settings.DATABASES, {REPLICA: REPLICA_CONFIG})
        self.patch.start()
        self.router = ReplicaRouter()

    def tearDown(self):
        self.patch.stop()

    def test_lists_and_reports_read_from_the_replica(self):
        self.assertEqual(self.router.db_for_read(ContentItem), REPLICA)

    def test_sessions_membership_and_notifications_read_from_the_primary(self):
        self.assertEqual(self.router.db_for_read(Membership), PRIMARY)
        from django.contrib.sessions.models import Session

        self.assertEqual(self.router.db_for_read(Session), PRIMARY)

    def test_writes_always_go_to_the_primary(self):
        self.assertEqual(self.router.db_for_write(ContentItem), PRIMARY)

    def test_a_read_inside_a_transaction_uses_the_primary(self):
        from django.db import transaction

        with transaction.atomic():
            self.assertEqual(self.router.db_for_read(ContentItem), PRIMARY)

    def test_primary_only_forces_the_primary(self):
        with primary_only():
            self.assertEqual(self.router.db_for_read(ContentItem), PRIMARY)
        self.assertEqual(self.router.db_for_read(ContentItem), REPLICA)

    def test_the_replica_never_runs_migrations(self):
        self.assertTrue(self.router.allow_migrate(PRIMARY, "production"))
        self.assertFalse(self.router.allow_migrate(REPLICA, "production"))


class AfterWriteTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)

    def test_a_change_sets_a_short_primary_window_for_the_person(self):
        with patch.dict(settings.DATABASES, {REPLICA: REPLICA_CONFIG}):
            self.client.force_login(self.owner.user)
            self.client.post(reverse("account"), {"language": "en"})
            until = self.client.session["primary_until"]
        self.assertGreater(until, time.time())
        self.assertLessEqual(until, time.time() + 6)

    def test_the_window_passes(self):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = self.owner.user
        request.session = {"primary_until": time.time() - 1}
        middleware = PrimaryAfterWriteMiddleware(lambda r: None)
        self.assertFalse(middleware._sticky(request))

    def test_a_person_inside_the_window_is_sticky(self):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = self.owner.user
        request.session = {"primary_until": time.time() + 3}
        middleware = PrimaryAfterWriteMiddleware(lambda r: None)
        self.assertTrue(middleware._sticky(request))

    def test_anonymous_requests_are_never_sticky(self):
        from django.contrib.auth.models import AnonymousUser

        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()
        request.session = {"primary_until": time.time() + 3}
        middleware = PrimaryAfterWriteMiddleware(lambda r: None)
        self.assertFalse(middleware._sticky(request))
