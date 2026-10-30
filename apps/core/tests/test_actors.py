from django.test import TestCase

from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.actors import actor_for
from apps.core.testing import make_membership, make_organization, make_owner


class ActorForTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.client_record = Client.objects.create(organization=self.agency, name="Padaria")

    def test_none_membership_gives_no_actor(self):
        self.assertIsNone(actor_for(None))

    def test_owner_sees_all_clients_without_listing_them(self):
        actor = actor_for(make_owner(self.agency))
        self.assertTrue(actor.sees_all_clients)
        self.assertFalse(actor.sees_only_assigned)

    def test_manager_carries_only_the_clients_they_were_given(self):
        manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        ClientAccess.objects.create(organization=self.agency, client=self.client_record, membership=manager)

        actor = actor_for(manager)

        self.assertFalse(actor.sees_all_clients)
        self.assertEqual(actor.client_ids, frozenset({self.client_record.pk}))

    def test_freelancer_is_limited_to_assigned_pieces(self):
        freelancer = make_membership(self.agency, Role.FREELANCER)
        actor = actor_for(freelancer)
        self.assertTrue(actor.sees_only_assigned)
        self.assertEqual(actor.organization_id, self.agency.pk)
