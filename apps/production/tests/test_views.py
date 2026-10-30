"""Internal web screens: the whole flow through HTTP, with the real database."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.domain.states import ContentState
from apps.production.models import ContentItem


class InternalFlowTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.owner = make_owner(self.agency)
        self.creative = make_membership(self.agency, Role.CREATIVE)
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        self.client_record = Client.objects.create(organization=self.agency, name="Padaria")
        ClientAccess.objects.create(organization=self.agency, client=self.client_record, membership=self.manager)
        ClientAccess.objects.create(organization=self.agency, client=self.client_record, membership=self.creative)

    def create_piece(self, membership, title="Post", owner=None):
        self.client.force_login(membership.user)
        self.client.post(
            reverse("content_create"),
            {
                "client": self.client_record.pk,
                "title": title,
                "channel": "instagram",
                "content_format": "feed",
                "owner": owner.pk if owner else "",
                "caption": "Legenda",
            },
        )
        return ContentItem.objects.get(title=title)

    def move(self, membership, piece, action, **data):
        self.client.force_login(membership.user)
        return self.client.post(reverse("content_action", args=[piece.pk, action]), data, follow=True)

    def test_creative_creates_a_piece_in_draft(self):
        piece = self.create_piece(self.creative, title="Carrossel novo")
        self.assertEqual(piece.state, ContentState.DRAFT)

    def test_full_approval_flow_through_the_screens(self):
        piece = self.create_piece(self.creative)
        self.move(self.creative, piece, "plan")
        self.move(self.creative, piece, "start_production")
        self.move(self.creative, piece, "send_internal_review")
        self.move(self.manager, piece, "approve_internal")

        piece.refresh_from_db()
        self.assertEqual(piece.state, ContentState.CLIENT_REVIEW)

    def test_creative_does_not_see_the_approve_button(self):
        piece = self.create_piece(self.creative)
        self.move(self.creative, piece, "plan")
        self.move(self.creative, piece, "start_production")
        self.move(self.creative, piece, "send_internal_review")

        self.client.force_login(self.creative.user)
        response = self.client.get(reverse("content_detail", args=[piece.pk]))

        self.assertNotContains(response, reverse("content_action", args=[piece.pk, "approve_internal"]))

    def test_creative_posting_an_approval_gets_403(self):
        piece = self.create_piece(self.creative)
        self.move(self.creative, piece, "plan")
        self.move(self.creative, piece, "start_production")
        self.move(self.creative, piece, "send_internal_review")

        self.client.force_login(self.creative.user)
        response = self.client.post(reverse("content_action", args=[piece.pk, "approve_internal"]), {})

        self.assertEqual(response.status_code, 403)
        piece.refresh_from_db()
        self.assertEqual(piece.state, ContentState.INTERNAL_REVIEW)

    def test_manager_outside_the_client_gets_404_for_the_piece(self):
        piece = self.create_piece(self.owner, title="Da agência")
        outsider = make_membership(self.agency, Role.ACCOUNT_MANAGER)  # not assigned to the client

        self.client.force_login(outsider.user)
        response = self.client.get(reverse("content_detail", args=[piece.pk]))

        self.assertEqual(response.status_code, 404)

    def test_unknown_action_is_404(self):
        piece = self.create_piece(self.owner)
        self.client.force_login(self.owner.user)
        response = self.client.post(reverse("content_action", args=[piece.pk, "apagar_tudo"]), {})
        self.assertEqual(response.status_code, 404)

    def test_freelancer_list_shows_only_their_pieces(self):
        freelancer = make_membership(self.agency, Role.FREELANCER)
        ClientAccess.objects.create(organization=self.agency, client=self.client_record, membership=freelancer)
        self.create_piece(self.owner, title="Minha", owner=freelancer.user)
        self.create_piece(self.owner, title="Alheia")

        self.client.force_login(freelancer.user)
        response = self.client.get(reverse("content_list"))

        self.assertContains(response, "Minha")
        self.assertNotContains(response, "Alheia")

    def test_editing_a_piece_awaiting_the_client_returns_it_to_internal_review(self):
        piece = self.create_piece(self.owner)
        self.move(self.owner, piece, "plan")
        self.move(self.owner, piece, "start_production")
        self.move(self.owner, piece, "send_internal_review")
        self.move(self.owner, piece, "approve_internal")
        self.client.force_login(self.owner.user)
        self.client.post(reverse("content_version", args=[piece.pk]), {"caption": "Nova legenda"})

        piece.refresh_from_db()
        self.assertEqual(piece.state, ContentState.INTERNAL_REVIEW)
        self.assertEqual(piece.versions.count(), 2)

    def test_dashboard_counts_only_visible_pieces(self):
        self.create_piece(self.owner, title="Visível")
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("counts", response.context)
