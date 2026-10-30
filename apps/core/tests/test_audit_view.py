from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Client
from apps.core.models import AuditEvent
from apps.core.testing import make_membership, make_organization, make_owner


class AuditLogScreenTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        Client.objects.create(organization=self.agency, name="Padaria")  # nothing audited by this alone
        AuditEvent.objects.create(
            organization=self.agency,
            actor=self.owner.user,
            action="content.state_changed",
            entity_type="ContentItem",
            entity_id=7,
            metadata={"from": "draft", "to": "planned"},
        )
        AuditEvent.objects.create(
            organization=self.agency,
            actor=self.owner.user,
            action="client.created",
            entity_type="Client",
            entity_id=1,
            metadata={},
        )

    def test_owner_sees_the_events_of_their_organization(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("audit_log"))
        self.assertContains(response, "content.state_changed")
        self.assertContains(response, "client.created")

    def test_filter_by_action_prefix(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("audit_log"), {"action": "content."})
        self.assertContains(response, "content.state_changed")
        self.assertNotContains(response, "client.created")

    def test_events_of_another_organization_are_not_shown(self):
        other = make_owner(make_organization("Outra"))
        AuditEvent.objects.create(
            organization=other.organization,
            actor=other.user,
            action="secret.other-agency",
            entity_type="Client",
            entity_id=9,
            metadata={},
        )
        self.client.force_login(self.owner.user)
        self.assertNotContains(self.client.get(reverse("audit_log")), "secret.other-agency")

    def test_only_owners_can_read_the_log(self):
        manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        self.client.force_login(manager.user)
        self.assertEqual(self.client.get(reverse("audit_log")).status_code, 403)
