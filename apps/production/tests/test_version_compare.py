"""Compare two versions of a piece side by side (TD-31, PRO-004 PROPOSAL)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.models import ContentItem


class VersionCompareTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.owner = make_owner(self.agency)
        self.creative = make_membership(self.agency, Role.CREATIVE)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.creative)
        self.piece = self.create_piece(self.bakery, "Post da semana")

    def create_piece(self, client_record, title):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("content_create"),
            {
                "client": client_record.pk,
                "title": title,
                "channel": "instagram",
                "content_format": "feed",
                "caption": "Legenda 1",
                "cta": "Peça já",
            },
        )
        return ContentItem.objects.get(title=title)

    def add_version(self, caption, cta="Peça já"):
        self.client.force_login(self.creative.user)
        self.client.post(
            reverse("content_version", args=[self.piece.pk]),
            {"caption": caption, "cta": cta, "script": "", "media_url": ""},
        )

    def test_one_version_shows_the_empty_state(self):
        response = self.client.get(reverse("content_compare", args=[self.piece.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A comparison needs at least two versions.")

    def test_by_default_compares_the_last_two_versions(self):
        self.add_version("Legenda 2")
        self.add_version("Legenda 3")

        response = self.client.get(reverse("content_compare", args=[self.piece.pk]))

        self.assertEqual(response.context["left"].number, 2)
        self.assertEqual(response.context["right"].number, 3)
        rows = {row["label"]: row for row in response.context["rows"]}
        self.assertTrue(rows["Caption"]["changed"])
        self.assertFalse(rows["Call to action (CTA)"]["changed"])
        self.assertContains(response, "Legenda 2")
        self.assertContains(response, "Legenda 3")

    def test_chosen_versions_are_compared(self):
        self.add_version("Legenda 2")
        self.add_version("Legenda 3")

        response = self.client.get(reverse("content_compare", args=[self.piece.pk]), {"from": "1", "to": "3"})

        self.assertEqual(response.context["left"].number, 1)
        self.assertEqual(response.context["right"].number, 3)

    def test_an_unknown_version_is_not_found(self):
        self.add_version("Legenda 2")

        response = self.client.get(reverse("content_compare", args=[self.piece.pk]), {"to": "9"})

        self.assertEqual(response.status_code, 404)

    def test_a_version_number_that_is_not_a_number_is_not_found(self):
        self.add_version("Legenda 2")

        response = self.client.get(reverse("content_compare", args=[self.piece.pk]), {"from": "abc"})

        self.assertEqual(response.status_code, 404)

    def test_a_piece_the_person_cannot_see_is_not_found(self):
        other_client = Client.objects.create(organization=self.agency, name="Loja")
        hidden = self.create_piece(other_client, "Segredo")
        self.client.force_login(self.creative.user)

        response = self.client.get(reverse("content_compare", args=[hidden.pk]))

        self.assertEqual(response.status_code, 404)

    def test_the_piece_page_links_to_the_comparison_when_there_are_two_versions(self):
        self.client.force_login(self.owner.user)
        self.assertNotContains(self.client.get(reverse("content_detail", args=[self.piece.pk])), "Compare versions")

        self.add_version("Legenda 2")
        self.client.force_login(self.owner.user)

        self.assertContains(self.client.get(reverse("content_detail", args=[self.piece.pk])), "Compare versions")
