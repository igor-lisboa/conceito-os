"""The client wall (SEC-017): a person sees only the clients they have access to.

One account manager ("ana") has access to the bakery only. Every screen that shows client
data is checked for the shop (another client). A detail page for the shop answers 404, and
a list shows nothing about the shop. Owners are not covered here: they see every client.
"""

from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import BrandAsset, Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.models import ContentItem
from apps.reports.models import Metric, MetricEntry, Platform
from apps.tasks.models import Task


class ClientWallTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria Bolo")
        self.shop = Client.objects.create(organization=self.agency, name="Loja Secreta")

        self.ana = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.ana)

        self.bakery_piece = self.create_piece(self.bakery, "Post da Padaria")
        self.shop_piece = self.create_piece(self.shop, "Post Segredo da Loja")
        self.shop_asset = BrandAsset.objects.create(
            organization=self.agency, client=self.shop, title="Logo da Loja", url="https://example.com/logo"
        )
        self.shop_metric = MetricEntry.objects.create(
            organization=self.agency,
            client=self.shop,
            platform=Platform.INSTAGRAM.value,
            metric=Metric.REACH.value,
            month=date(2026, 10, 1),
            value=987654,
        )
        self.shop_task = Task.objects.create(
            organization=self.agency, client=self.shop, title="Tarefa Secreta da Loja", owner=self.owner.user
        )

    def create_piece(self, client_record, title):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("content_create"),
            {
                "client": client_record.pk,
                "title": title,
                "channel": "instagram",
                "content_format": "feed",
                "caption": "Legenda",
            },
        )
        return ContentItem.objects.get(title=title)

    def sign_in_as_ana(self):
        self.client.force_login(self.ana.user)

    # --- detail pages: another client's record is "not found" ----------------------------

    def test_another_clients_detail_pages_are_not_found(self):
        self.sign_in_as_ana()
        urls = [
            reverse("client_detail", args=[self.shop.pk]),
            reverse("client_briefing", args=[self.shop.pk]),
            reverse("client_asset_create", args=[self.shop.pk]),
            reverse("content_detail", args=[self.shop_piece.pk]),
            reverse("content_compare", args=[self.shop_piece.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_another_clients_actions_are_not_found(self):
        self.sign_in_as_ana()
        self.assertEqual(
            self.client.post(reverse("content_duplicate", args=[self.shop_piece.pk])).status_code, 404
        )
        self.assertEqual(
            self.client.post(reverse("content_comment", args=[self.shop_piece.pk]), {"body": "oi"}).status_code, 404
        )
        self.assertEqual(
            self.client.post(
                reverse("content_action", args=[self.shop_piece.pk, "plan"]), {}
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse("content_version", args=[self.shop_piece.pk]), {"caption": "invadir"}
            ).status_code,
            404,
        )
        self.shop_piece.refresh_from_db()
        self.assertNotEqual(self.shop_piece.versions.order_by("-number").first().caption, "invadir")

    # --- lists and counts: nothing about the shop -------------------------------------

    def test_client_list_does_not_show_the_shop(self):
        self.sign_in_as_ana()
        response = self.client.get(reverse("client_list"))
        self.assertContains(response, "Padaria Bolo")
        self.assertNotContains(response, "Loja Secreta")

    def test_content_lists_do_not_show_the_shop_piece(self):
        self.sign_in_as_ana()
        for name in ["content_list", "content_calendar", "content_board"]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertNotContains(response, "Post Segredo da Loja")

    def test_dashboard_counts_only_visible_pieces(self):
        self.sign_in_as_ana()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["counts"]["internal_review"], 0)
        self.assertEqual(response.context["counts"]["client_review"], 0)

    def test_report_for_another_client_shows_no_values(self):
        self.sign_in_as_ana()
        response = self.client.get(reverse("report"), {"client": self.shop.pk, "month": "2026-10"})
        self.assertNotContains(response, "Loja Secreta")
        self.assertNotContains(response, "987654")
        self.assertEqual(response.context["client"].pk, self.bakery.pk)

    def test_tasks_of_another_client_are_not_listed(self):
        self.sign_in_as_ana()
        response = self.client.get(reverse("task_list"))
        self.assertNotContains(response, "Tarefa Secreta da Loja")

    def test_the_shop_logo_link_is_not_listed_in_the_bakery_library(self):
        self.sign_in_as_ana()
        response = self.client.get(reverse("client_detail", args=[self.bakery.pk]))
        self.assertNotContains(response, "Logo da Loja")
        self.assertNotContains(response, "Loja Secreta")

    def test_the_client_portal_of_the_shop_never_shows_the_bakery(self):
        shop_user = make_membership(self.agency, Role.CLIENT, username="cliente-loja")
        ClientAccess.objects.create(organization=self.agency, client=self.shop, membership=shop_user)
        self.client.force_login(shop_user.user)

        response = self.client.get(reverse("portal_list"))
        self.assertNotContains(response, "Post da Padaria")
        self.assertEqual(self.client.get(reverse("portal_detail", args=[self.bakery_piece.pk])).status_code, 404)
