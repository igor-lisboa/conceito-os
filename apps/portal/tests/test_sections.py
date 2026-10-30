"""Client portal sections: calendar, results, files and contact (TD-26)."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.roles import Role
from apps.clients.models import BrandAsset, Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.tests.test_comments_and_planning import ContentFixtureMixin
from apps.reports.models import MetricEntry


class PortalSectionsTests(ContentFixtureMixin, TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.clinic = Client.objects.create(organization=self.agency, name="Clínica")
        self.portal_user = make_membership(self.agency, Role.CLIENT)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.portal_user)
        self.client.force_login(self.portal_user.user)

    def test_calendar_shows_only_the_clients_scheduled_pieces(self):
        when = timezone.now() + timedelta(days=2)
        self.make_piece(self.bakery, self.owner, title="Da padaria", scheduled_in=when)
        self.make_piece(self.clinic, self.owner, title="Da clínica", scheduled_in=when)

        response = self.client.get(reverse("portal_calendar"))

        self.assertContains(response, "Da padaria")
        self.assertNotContains(response, "Da clínica")

    def test_results_show_entered_values_and_nd_for_the_rest(self):
        month = timezone.localdate().replace(day=1)
        MetricEntry.objects.create(
            organization=self.agency, client=self.bakery, platform="instagram", metric="reach",
            month=month, value=4200,
        )
        response = self.client.get(reverse("portal_results"))

        blocks = {block["client"].name: block["rows"] for block in response.context["blocks"]}
        self.assertEqual(blocks.keys(), {"Padaria"})
        reach = next(row for row in blocks["Padaria"] if row["metric"] == "Reach")
        self.assertEqual(reach["value"], 4200)
        saves = next(row for row in blocks["Padaria"] if row["metric"] == "Saves")
        self.assertEqual(saves["value"], "N/D")

    def test_results_never_show_another_brand(self):
        MetricEntry.objects.create(
            organization=self.agency, client=self.clinic, platform="instagram", metric="reach",
            month=timezone.localdate().replace(day=1), value=999,
        )
        response = self.client.get(reverse("portal_results"))
        self.assertNotContains(response, "999")

    def test_files_show_only_links_of_the_clients_brands(self):
        BrandAsset.objects.create(organization=self.agency, client=self.bakery, title="Logo da padaria", url="https://drive.example.com/a")
        BrandAsset.objects.create(organization=self.agency, client=self.clinic, title="Logo da clínica", url="https://drive.example.com/b")

        response = self.client.get(reverse("portal_files"))

        self.assertContains(response, "Logo da padaria")
        self.assertNotContains(response, "Logo da clínica")

    def test_contact_page_shows_the_configured_address(self):
        response = self.client.get(reverse("portal_contact"))
        self.assertContains(response, "contato@conceito.com.br")

    def test_team_members_cannot_use_the_portal_sections(self):
        creative = make_membership(self.agency, Role.CREATIVE)
        self.client.force_login(creative.user)
        self.assertEqual(self.client.get(reverse("portal_results")).status_code, 403)
