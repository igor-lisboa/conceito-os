"""Board drag (D-28): a card moves only along the manual moves (PD-41). Filters collapse on phones (D-29)."""

from django.test import TestCase
from django.urls import reverse

from apps.clients.models import Client
from apps.core.actors import actor_for
from apps.core.testing import make_organization, make_owner
from apps.production.composition import build_content_service
from apps.production.domain.content import Channel, ContentFormat, VersionData
from apps.production.domain.states import MANUAL_MOVES, ContentState
from apps.production.models import ContentItem
from apps.production.planning import BOARD_DRAG_ACTIONS


class BoardDragRuleTests(TestCase):
    def test_the_board_drag_moves_are_exactly_the_manual_moves(self):
        self.assertEqual(set(BOARD_DRAG_ACTIONS), set(MANUAL_MOVES))


class BoardDragScreenTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.client_record = Client.objects.create(
            organization=self.agency, name="Padaria", client_approval_required=False
        )
        self.service = build_content_service()
        self.draft_id = self._create("Rascunho")
        self.approved_id = self._create("Aprovado")
        actor = actor_for(self.owner)
        for target in (ContentState.PLANNED, ContentState.IN_PRODUCTION, ContentState.INTERNAL_REVIEW):
            self.service.move_to(actor, self.approved_id, target)
        self.service.decide_internal(actor, self.approved_id, approve=True)
        self.client.force_login(self.owner.user)

    def _create(self, title):
        return self.service.create(
            actor_for(self.owner),
            client_id=self.client_record.pk,
            title=title,
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="Legenda"),
        )

    def test_a_draft_card_can_be_dragged_and_an_approved_card_cannot(self):
        response = self.client.get(reverse("content_board"))

        self.assertContains(response, f'data-content-id="{self.draft_id}"')
        self.assertNotContains(response, f'data-content-id="{self.approved_id}"')

    def test_the_drop_uses_the_same_action_as_the_piece_page(self):
        response = self.client.get(reverse("content_board"))

        self.assertContains(response, "/acao/placeholder/")
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_a_drop_moves_the_card_and_returns_to_the_board(self):
        response = self.client.post(
            reverse("content_action", args=[self.draft_id, "plan"]),
            {"next": reverse("content_board")},
        )

        self.assertRedirects(response, reverse("content_board"))
        self.assertEqual(ContentItem.objects.get(pk=self.draft_id).state, ContentState.PLANNED.value)

    def test_an_unsafe_return_address_is_ignored(self):
        response = self.client.post(
            reverse("content_action", args=[self.draft_id, "plan"]),
            {"next": "https://evil.example.com/"},
        )

        self.assertRedirects(response, reverse("content_detail", args=[self.draft_id]))

    def test_the_board_filters_are_open_only_when_a_filter_is_set(self):
        closed = self.client.get(reverse("content_board"))
        self.assertContains(closed, '<details class="filters card">')

        opened = self.client.get(reverse("content_board"), {"client": self.client_record.pk})
        self.assertContains(opened, '<details class="filters card" open>')

    def test_an_organization_outsider_cannot_drag_a_card_of_another_agency(self):
        other = make_owner(make_organization("Outra agência"))
        self.client.force_login(other.user)

        response = self.client.post(
            reverse("content_action", args=[self.draft_id, "plan"]),
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(ContentItem.objects.get(pk=self.draft_id).state, ContentState.DRAFT.value)
