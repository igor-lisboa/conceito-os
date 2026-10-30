from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from clients import services
from clients.models import Client
from core.testing import make_membership, make_organization, make_owner


class ClientViewsTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.owner = make_owner(self.agency)
        self.client_record = services.create_client(self.owner, name="Padaria")

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(reverse("client_list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('client_list')}")

    def test_owner_can_open_client_detail(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("client_detail", args=[self.client_record.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Padaria")

    def test_client_from_another_agency_returns_404_not_403(self):
        # 404 (not 403) so an attacker cannot discover which IDs exist.
        other_agency = make_organization("Agência B")
        other_owner = make_owner(other_agency)
        self.client.force_login(other_owner.user)

        response = self.client.get(reverse("client_detail", args=[self.client_record.pk]))
        self.assertEqual(response.status_code, 404)

    def test_client_role_cannot_use_internal_pages(self):
        portal_user = make_membership(self.agency, Role.CLIENT)
        self.client.force_login(portal_user.user)

        response = self.client.get(reverse("client_list"))
        self.assertEqual(response.status_code, 403)

    def test_owner_creates_client_through_form(self):
        self.client.force_login(self.owner.user)
        response = self.client.post(
            reverse("client_create"),
            {"name": "Clínica Sorriso", "client_approval_required": "on"},
        )
        self.assertRedirects(response, reverse("client_list"))
        self.assertTrue(Client.objects.filter(name="Clínica Sorriso", organization=self.agency).exists())

    def test_creative_cannot_reach_create_form(self):
        creative = make_membership(self.agency, Role.CREATIVE)
        self.client.force_login(creative.user)
        response = self.client.get(reverse("client_create"))
        self.assertEqual(response.status_code, 403)

    def test_briefing_form_saves_answers(self):
        self.client.force_login(self.owner.user)
        response = self.client.post(
            reverse("client_briefing", args=[self.client_record.pk]),
            {
                "objective": "Aumentar pedidos",
                "audience": "",
                "tone_of_voice": "",
                "competitors": "",
                "notes": "",
            },
        )
        self.assertRedirects(response, reverse("client_detail", args=[self.client_record.pk]))
        self.client_record.briefing.refresh_from_db()
        self.assertEqual(self.client_record.briefing.objective, "Aumentar pedidos")
