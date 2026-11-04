"""The audit trail is append-only (SEC-007, PRM-006): rows are never changed or removed."""

from django.test import TestCase

from apps.core.models import AuditEvent
from apps.core.testing import make_organization, make_owner


class AuditAppendOnlyTests(TestCase):
    def setUp(self):
        self.owner = make_owner(make_organization())
        self.event = AuditEvent.objects.create(
            organization=self.owner.organization,
            actor=self.owner.user,
            action="client.created",
            entity_type="Client",
            entity_id=self.owner.pk,
        )

    def test_a_saved_event_cannot_be_edited(self):
        self.event.action = "changed"
        with self.assertRaises(RuntimeError):
            self.event.save()

    def test_a_saved_event_cannot_be_deleted(self):
        with self.assertRaises(RuntimeError):
            self.event.delete()

    def test_bulk_delete_is_refused(self):
        with self.assertRaises(RuntimeError):
            AuditEvent.objects.filter(pk=self.event.pk).delete()
        self.assertTrue(AuditEvent.objects.filter(pk=self.event.pk).exists())

    def test_bulk_update_is_refused(self):
        with self.assertRaises(RuntimeError):
            AuditEvent.objects.filter(pk=self.event.pk).update(action="changed")
        self.assertEqual(AuditEvent.objects.get(pk=self.event.pk).action, "client.created")

    def test_creating_events_still_works(self):
        AuditEvent.objects.create(
            organization=self.owner.organization,
            actor=self.owner.user,
            action="client.archived",
            entity_type="Client",
            entity_id=self.owner.pk,
        )
        self.assertEqual(AuditEvent.objects.filter(action="client.archived").count(), 1)
