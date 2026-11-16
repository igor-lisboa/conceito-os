"""Deleting an organization or a user cannot remove or rewrite audit rows (SEC-007)."""

from django.db.models import ProtectedError
from django.test import TestCase

from apps.accounts.models import Organization, User
from apps.core.models import AuditEvent
from apps.core.testing import make_organization, make_owner


class AuditRowsBlockDeletionTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.event = AuditEvent.objects.create(
            organization=self.agency,
            actor=self.owner.user,
            action="client.created",
            entity_type="client",
            entity_id=self.agency.pk,
            metadata={},
        )

    def test_an_organization_with_audit_rows_cannot_be_deleted(self):
        with self.assertRaises(ProtectedError):
            Organization.objects.filter(pk=self.agency.pk).delete()

        self.assertTrue(AuditEvent.objects.filter(pk=self.event.pk).exists())

    def test_a_user_who_acted_cannot_be_deleted(self):
        with self.assertRaises(ProtectedError):
            User.objects.filter(pk=self.owner.user.pk).delete()

        self.event.refresh_from_db()
        self.assertEqual(self.event.actor_id, self.owner.user.pk)
