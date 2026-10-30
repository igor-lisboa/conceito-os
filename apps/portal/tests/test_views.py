"""Client portal: what a client can see and decide, and what stays hidden."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.actors import actor_for
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.composition import build_content_service
from apps.production.domain.content import Channel, ContentFormat, VersionData
from apps.production.domain.states import ContentState
from apps.production.models import ContentItem


class PortalTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.clinic = Client.objects.create(organization=self.agency, name="Clínica")
        self.client_user = make_membership(self.agency, Role.CLIENT)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.client_user)
        self.service = build_content_service()

        self.bakery_piece = self.create_piece(self.bakery, "Pão de queijo")
        self.clinic_piece = self.create_piece(self.clinic, "Clareamento")
        self.send_to_client_review(self.bakery_piece, comment_internal="Ajustar tom: segredo-interno")
        self.send_to_client_review(self.clinic_piece)

    def create_piece(self, client, title):
        content_id = self.service.create(
            actor_for(self.owner),
            client_id=client.pk,
            title=title,
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="Legenda da peça"),
        )
        return ContentItem.objects.get(pk=content_id)

    def send_to_client_review(self, piece, comment_internal=""):
        owner = actor_for(self.owner)
        self.service.move_to(owner, piece.pk, ContentState.PLANNED)
        self.service.move_to(owner, piece.pk, ContentState.IN_PRODUCTION)
        self.service.move_to(owner, piece.pk, ContentState.INTERNAL_REVIEW)
        self.service.decide_internal(owner, piece.pk, approve=True, comment=comment_internal)

    def test_client_list_shows_only_their_brand_pieces_in_review(self):
        self.client.force_login(self.client_user.user)
        response = self.client.get(reverse("portal_list"))

        self.assertContains(response, "Pão de queijo")
        self.assertNotContains(response, "Clareamento")

    def test_client_cannot_open_another_brands_piece(self):
        self.client.force_login(self.client_user.user)
        response = self.client.get(reverse("portal_detail", args=[self.clinic_piece.pk]))
        self.assertEqual(response.status_code, 404)

    def test_internal_comments_never_reach_the_portal(self):
        self.client.force_login(self.client_user.user)
        response = self.client.get(reverse("portal_detail", args=[self.bakery_piece.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "segredo-interno")

    def test_client_approves_through_the_portal(self):
        self.client.force_login(self.client_user.user)
        self.client.post(
            reverse("portal_detail", args=[self.bakery_piece.pk]),
            {"decision": "approve", "comment": ""},
        )

        self.bakery_piece.refresh_from_db()
        self.assertEqual(self.bakery_piece.state, ContentState.APPROVED)

    def test_requesting_changes_without_a_comment_changes_nothing(self):
        self.client.force_login(self.client_user.user)
        self.client.post(
            reverse("portal_detail", args=[self.bakery_piece.pk]),
            {"decision": "request_changes", "comment": ""},
            follow=True,
        )

        self.bakery_piece.refresh_from_db()
        self.assertEqual(self.bakery_piece.state, ContentState.CLIENT_REVIEW)

    def test_requesting_changes_with_a_comment_is_recorded(self):
        self.client.force_login(self.client_user.user)
        self.client.post(
            reverse("portal_detail", args=[self.bakery_piece.pk]),
            {"decision": "request_changes", "comment": "Mais leve, por favor"},
        )

        self.bakery_piece.refresh_from_db()
        self.assertEqual(self.bakery_piece.state, ContentState.CHANGES_REQUESTED)
        response = self.client.get(reverse("portal_detail", args=[self.bakery_piece.pk]))
        self.assertContains(response, "Mais leve, por favor")

    def test_internal_user_cannot_use_the_portal(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("portal_list"))
        self.assertEqual(response.status_code, 403)
