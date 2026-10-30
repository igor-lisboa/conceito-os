from django.db import IntegrityError
from django.test import TestCase

from accounts.roles import Role
from clients import services
from clients.models import Client, ClientAccess
from clients.queries import visible_clients
from core.exceptions import Forbidden, NotFound
from core.models import AuditEvent
from core.testing import make_membership, make_organization, make_owner


class CreateClientTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)

    def test_owner_creates_client_with_empty_briefing_and_audit_event(self):
        client = services.create_client(self.owner, name="Padaria Pão Quente")

        self.assertEqual(client.organization, self.agency)
        self.assertTrue(client.client_approval_required)
        self.assertTrue(hasattr(client, "briefing"))
        self.assertTrue(
            AuditEvent.objects.filter(action=services.CLIENT_CREATED, entity_id=client.pk).exists()
        )

    def test_creator_gets_access_to_the_new_client(self):
        manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)

        client = services.create_client(manager, name="Clínica Sorriso")

        self.assertTrue(ClientAccess.objects.filter(client=client, membership=manager).exists())
        self.assertTrue(visible_clients(manager).filter(pk=client.pk).exists())

    def test_client_approval_can_be_turned_off(self):
        client = services.create_client(self.owner, name="Loja", client_approval_required=False)
        self.assertFalse(client.client_approval_required)

    def test_creative_cannot_create_client(self):
        creative = make_membership(self.agency, Role.CREATIVE)
        with self.assertRaises(Forbidden):
            services.create_client(creative, name="Não deveria existir")
        self.assertFalse(Client.objects.filter(name="Não deveria existir").exists())

    def test_duplicate_name_in_same_organization_is_rejected(self):
        services.create_client(self.owner, name="Padaria")
        with self.assertRaises(IntegrityError):
            services.create_client(self.owner, name="Padaria")

    def test_same_name_in_another_organization_is_allowed(self):
        services.create_client(self.owner, name="Padaria")
        other_owner = make_owner(make_organization("Agência B"))
        services.create_client(other_owner, name="Padaria")
        self.assertEqual(Client.objects.filter(name="Padaria").count(), 2)


class UpdateBriefingTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.client_record = services.create_client(self.owner, name="Padaria")

    def test_briefing_answers_are_saved_and_audited(self):
        services.update_briefing(self.owner, self.client_record, objective="Vender mais pães na manhã")

        self.client_record.briefing.refresh_from_db()
        self.assertEqual(self.client_record.briefing.objective, "Vender mais pães na manhã")
        event = AuditEvent.objects.get(action=services.BRIEFING_UPDATED)
        self.assertEqual(event.metadata, {"fields": ["objective"]})

    def test_manager_outside_client_scope_cannot_edit_briefing(self):
        outsider = make_membership(self.agency, Role.ACCOUNT_MANAGER)  # no ClientAccess row
        with self.assertRaises(NotFound):
            services.update_briefing(outsider, self.client_record, objective="Invasão")

        self.client_record.briefing.refresh_from_db()
        self.assertEqual(self.client_record.briefing.objective, "")

    def test_freelancer_cannot_edit_briefing_even_with_client_access(self):
        # Freelancers can see a client they are assigned to, but briefing editing is a
        # capability they do not have.
        freelancer = make_membership(self.agency, Role.FREELANCER)
        ClientAccess.objects.create(
            organization=self.agency, client=self.client_record, membership=freelancer
        )
        with self.assertRaises(Forbidden):
            services.update_briefing(freelancer, self.client_record, objective="Não pode")
