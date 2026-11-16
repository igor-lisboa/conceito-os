"""Campaigns of a client (CAL-001, decided 2026-11-16: add a campaign entity now)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Campaign, Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.models import ContentItem
from apps.production.planning import PlanningFilterForm


class CampaignTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.shop = Client.objects.create(organization=self.agency, name="Loja")
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)
        self.bakery_campaign = Campaign.objects.create(
            organization=self.agency, client=self.bakery, name="Pascoa"
        )
        self.shop_campaign = Campaign.objects.create(organization=self.agency, client=self.shop, name="Natal Secreta")

    def new_piece(self, client_record, title, campaign=None):
        return ContentItem.objects.create(
            organization=self.agency, client=client_record, campaign=campaign, title=title,
            channel="instagram", content_format="feed",
        )

    def test_the_owner_creates_a_campaign_for_a_client(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("client_campaigns", args=[self.bakery.pk]),
            {"name": "Dia das Maes", "starts_on": "2026-05-01", "ends_on": "2026-05-10"},
        )
        self.assertTrue(Campaign.objects.filter(client=self.bakery, name="Dia das Maes").exists())

    def test_the_end_date_cannot_be_before_the_start_date(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("client_campaigns", args=[self.bakery.pk]),
            {"name": "Errada", "starts_on": "2026-05-10", "ends_on": "2026-05-01"},
        )
        self.assertFalse(Campaign.objects.filter(name="Errada").exists())

    def test_a_person_without_the_client_cannot_see_its_campaigns(self):
        self.client.force_login(self.manager.user)
        self.assertEqual(self.client.get(reverse("client_campaigns", args=[self.shop.pk])).status_code, 404)
        self.assertEqual(
            self.client.post(reverse("client_campaigns", args=[self.shop.pk]), {"name": "Invasao"}).status_code,
            404,
        )
        self.assertFalse(Campaign.objects.filter(name="Invasao").exists())

    def test_a_freelancer_cannot_create_a_campaign(self):
        freelancer = make_membership(self.agency, Role.FREELANCER, username="fran")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=freelancer)
        self.client.force_login(freelancer.user)
        response = self.client.post(reverse("client_campaigns", args=[self.bakery.pk]), {"name": "Nao"})
        self.assertEqual(response.status_code, 403)

    def test_a_piece_takes_a_campaign_of_its_own_client(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("content_create"),
            {
                "client": self.bakery.pk, "campaign": self.bakery_campaign.pk, "title": "Ovo de Pascoa",
                "channel": "instagram", "content_format": "feed", "caption": "Legenda",
            },
        )
        self.assertEqual(ContentItem.objects.get(title="Ovo de Pascoa").campaign_id, self.bakery_campaign.pk)

    def test_a_piece_cannot_take_a_campaign_of_another_client(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("content_create"),
            {
                "client": self.bakery.pk, "campaign": self.shop_campaign.pk, "title": "Misturado",
                "channel": "instagram", "content_format": "feed", "caption": "Legenda",
            },
        )
        self.assertFalse(ContentItem.objects.filter(title="Misturado").exists())

    def test_the_piece_form_offers_only_campaigns_of_visible_clients(self):
        from apps.production.forms import ContentForm

        form = ContentForm(membership=self.manager)
        self.assertIn(self.bakery_campaign, form.fields["campaign"].queryset)
        self.assertNotIn(self.shop_campaign, form.fields["campaign"].queryset)

    def test_the_calendar_filter_keeps_only_the_chosen_campaign(self):
        in_campaign = self.new_piece(self.bakery, "Na campanha", self.bakery_campaign)
        self.new_piece(self.bakery, "Sem campanha")
        form = PlanningFilterForm({"campaign": self.bakery_campaign.pk}, membership=self.owner, show_state=True)

        result = list(form.apply(ContentItem.objects.all()))

        self.assertEqual(result, [in_campaign])

    def test_a_deleted_campaign_is_hidden_but_pieces_keep_it(self):
        piece = self.new_piece(self.bakery, "Antigo", self.bakery_campaign)

        self.bakery_campaign.delete()

        self.assertFalse(Campaign.objects.filter(pk=self.bakery_campaign.pk).exists())
        self.assertTrue(Campaign.all_objects.filter(pk=self.bakery_campaign.pk).exists())
        piece.refresh_from_db()
        self.assertEqual(piece.campaign_id, self.bakery_campaign.pk)
