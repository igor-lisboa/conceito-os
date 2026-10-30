"""Brand library: links to files kept elsewhere (TD-02, PD-03)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import BrandAsset, Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner


class BrandLibraryTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)

    def add(self, user, client=None, **data):
        self.client.force_login(user)
        payload = {"title": "Logo principal", "kind": "logo", "url": "https://drive.example.com/logo"}
        payload.update(data)
        return self.client.post(reverse("client_asset_create", args=[(client or self.bakery).pk]), payload)

    def test_owner_adds_a_link_and_it_shows_on_the_client_page(self):
        response = self.add(self.owner.user)

        self.assertRedirects(response, reverse("client_detail", args=[self.bakery.pk]))
        self.assertTrue(BrandAsset.objects.filter(client=self.bakery, title="Logo principal").exists())
        self.assertContains(self.client.get(reverse("client_detail", args=[self.bakery.pk])), "Logo principal")

    def test_a_link_must_be_a_web_address(self):
        self.add(self.owner.user, url="not a link")
        self.assertFalse(BrandAsset.objects.exists())

    def test_someone_without_access_to_the_client_gets_404(self):
        outsider = make_membership(self.agency, Role.CREATIVE)
        self.assertEqual(self.add(outsider.user).status_code, 404)
        self.assertFalse(BrandAsset.objects.exists())

    def test_freelancers_cannot_add_links(self):
        freelancer = make_membership(self.agency, Role.FREELANCER)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=freelancer)
        self.assertEqual(self.add(freelancer.user).status_code, 403)

    def test_a_link_cannot_be_added_to_an_archived_client(self):
        self.bakery.archived_at = self.bakery.created_at
        self.bakery.save()
        self.assertEqual(self.add(self.owner.user).status_code, 404)
