"""Who gets which notification, and that each one is written only once."""

import uuid

from django.core import mail
from django.test import TestCase

from accounts.roles import Role
from clients.models import Client, ClientAccess
from core.testing import make_membership, make_organization, make_owner
from notifications.adapters import DjangoNotifier
from notifications.models import Notification

CONTENT_ID = uuid.UUID("6f1c2a4e-9b3d-4e8f-8a7c-1d2e3f4a5b6c")


class NotifierRecipientsTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.owner = make_owner(self.agency)
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        self.other_manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        self.creative = make_membership(self.agency, Role.CREATIVE)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.clinic = Client.objects.create(organization=self.agency, name="Clínica")
        self.client_user = make_membership(self.agency, Role.CLIENT)
        self.other_client_user = make_membership(self.agency, Role.CLIENT)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.client_user)
        ClientAccess.objects.create(organization=self.agency, client=self.clinic, membership=self.other_manager)
        ClientAccess.objects.create(
            organization=self.agency, client=self.clinic, membership=self.other_client_user
        )
        self.notifier = DjangoNotifier()

    def notify(self, kind, *, client=None, owner_id=None, actor=None, key="k1", extra=None):
        client = client or self.bakery
        return self.notifier.notify(
            kind=kind,
            organization_id=self.agency.pk,
            client_id=client.pk,
            content_id=CONTENT_ID,
            title="Pão de queijo",
            owner_id=owner_id,
            actor_user_id=actor.user_id if actor else None,
            event_key=key,
            extra=extra,
        )

    def recipients(self):
        return set(Notification.objects.values_list("recipient_id", flat=True))

    def test_internal_review_reaches_owner_and_managers_of_that_brand_only(self):
        self.notify("internal_review", actor=self.creative)

        self.assertEqual(self.recipients(), {self.owner.user_id, self.manager.user_id})

    def test_client_review_reaches_only_the_clients_of_that_brand(self):
        self.notify("client_review", actor=self.manager)

        self.assertEqual(self.recipients(), {self.client_user.user_id})

    def test_the_person_who_caused_the_event_is_not_notified(self):
        self.notify("internal_review", actor=self.owner)

        self.assertNotIn(self.owner.user_id, self.recipients())
        self.assertIn(self.manager.user_id, self.recipients())

    def test_a_rejection_goes_to_the_person_who_made_the_piece(self):
        self.notify("internal_rejected", actor=self.manager, owner_id=self.creative.user_id)

        self.assertEqual(self.recipients(), {self.creative.user_id})

    def test_the_same_event_is_never_written_twice(self):
        self.notify("internal_review", actor=self.creative, key="same")
        self.notify("internal_review", actor=self.creative, key="same")

        self.assertEqual(Notification.objects.count(), 2)  # owner + manager, once each

    def test_the_message_contains_the_client_name_and_the_title(self):
        self.notify("client_review", actor=self.manager)

        notification = Notification.objects.get(recipient=self.client_user.user)
        self.assertEqual(notification.message, "“Pão de queijo” for Padaria is waiting for your approval.")
        self.assertEqual(notification.url, f"/portal/{CONTENT_ID}/")

    def test_failure_reason_appears_in_the_message(self):
        self.notify("publish_failed", actor=self.creative, extra={"reason": "Token expirado"})

        message = Notification.objects.first().message
        self.assertIn("Token expirado", message)

    def test_email_is_sent_after_commit_to_each_recipient(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.notify("client_review", actor=self.manager)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.client_user.user.email])
        self.assertIn(f"/portal/{CONTENT_ID}/", mail.outbox[0].body)

    def test_unknown_kind_is_refused(self):
        with self.assertRaises(ValueError):
            self.notify("not-a-kind", actor=self.manager)
        self.assertFalse(Notification.objects.exists())

    def test_people_in_another_agency_are_never_notified(self):
        outsider = make_owner(make_organization("Outra agência"))
        self.notify("internal_review", actor=self.creative)

        self.assertFalse(Notification.objects.filter(recipient=outsider.user).exists())
        self.assertFalse(Notification.objects.exclude(organization=self.agency).exists())
