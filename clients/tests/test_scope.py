from django.test import TestCase

from accounts.models import Role
from clients.models import Client, ClientAccess
from clients.queries import visible_clients
from core.testing import make_membership, make_organization, make_owner


class VisibleClientsTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.other_agency = make_organization("Agência B")
        self.owner = make_owner(self.agency)
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        self.assigned = Client.objects.create(organization=self.agency, name="Padaria")
        self.unassigned = Client.objects.create(organization=self.agency, name="Clínica")
        self.foreign = Client.objects.create(organization=self.other_agency, name="Loja de outra agência")
        ClientAccess.objects.create(organization=self.agency, client=self.assigned, membership=self.manager)

    def test_owner_sees_every_client_of_their_own_organization(self):
        names = set(visible_clients(self.owner).values_list("name", flat=True))
        self.assertEqual(names, {"Padaria", "Clínica"})

    def test_account_manager_sees_only_assigned_clients(self):
        names = list(visible_clients(self.manager).values_list("name", flat=True))
        self.assertEqual(names, ["Padaria"])

    def test_client_from_another_organization_is_never_visible(self):
        self.assertFalse(visible_clients(self.owner).filter(pk=self.foreign.pk).exists())
        self.assertFalse(visible_clients(self.manager).filter(pk=self.foreign.pk).exists())

    def test_membership_without_access_rows_sees_nothing(self):
        creative = make_membership(self.agency, Role.CREATIVE)
        self.assertFalse(visible_clients(creative).exists())
