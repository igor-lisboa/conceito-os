"""Planned dates (PRO-015) and their lock once the client sees the piece (PRO-016)."""

from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.roles import Role
from apps.clients.models import Client
from apps.core.actors import actor_for
from apps.core.exceptions import DomainError
from apps.core.models import AuditEvent
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.composition import build_content_service
from apps.production.domain.content import Channel, ContentFormat, VersionData
from apps.production.domain.states import ContentState
from apps.production.models import ContentItem

PLANNED = timezone.make_aware(datetime(2030, 3, 10, 9, 0))
MOVED = timezone.make_aware(datetime(2030, 3, 12, 14, 30))


class PlannedDateTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.client_record = Client.objects.create(
            organization=self.agency, name="Padaria", client_approval_required=True
        )
        self.service = build_content_service()
        self.piece_id = self.service.create(
            actor_for(self.owner),
            client_id=self.client_record.pk,
            title="Post de março",
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="Legenda"),
        )
        self.service.reschedule(actor_for(self.owner), self.piece_id, when=PLANNED, reason="Primeira data")

    def _move_to_internal_review(self):
        actor = actor_for(self.owner)
        self.service.move_to(actor, self.piece_id, ContentState.PLANNED)
        self.service.move_to(actor, self.piece_id, ContentState.IN_PRODUCTION)
        self.service.move_to(actor, self.piece_id, ContentState.INTERNAL_REVIEW)

    def test_a_planned_date_is_saved_and_the_reason_is_recorded(self):
        piece = ContentItem.objects.get(pk=self.piece_id)
        self.assertEqual(piece.planned_for, PLANNED)

        self.service.reschedule(actor_for(self.owner), self.piece_id, when=MOVED, reason="Feriado no dia 10")

        piece.refresh_from_db()
        self.assertEqual(piece.planned_for, MOVED)
        # Ids are UUIDs (DAT-010), so look the event up by its reason rather than by "latest id".
        event = AuditEvent.objects.get(action="content.planned_date_changed", metadata__reason="Feriado no dia 10")
        self.assertEqual(event.metadata["from"], PLANNED.isoformat())
        self.assertEqual(event.metadata["to"], MOVED.isoformat())

    def test_the_reason_is_required(self):
        with self.assertRaisesMessage(DomainError, "Explain why the date changes."):
            self.service.reschedule(actor_for(self.owner), self.piece_id, when=MOVED, reason="   ")

    def test_the_date_is_required(self):
        with self.assertRaisesMessage(DomainError, "Enter the planned date."):
            self.service.reschedule(actor_for(self.owner), self.piece_id, when=None, reason="Motivo")

    def test_the_date_is_locked_once_the_piece_reaches_the_client(self):
        self._move_to_internal_review()
        self.service.decide_internal(actor_for(self.owner), self.piece_id, approve=True)
        self.assertEqual(ContentItem.objects.get(pk=self.piece_id).state, ContentState.CLIENT_REVIEW.value)

        with self.assertRaisesMessage(DomainError, "The planned date is locked once the piece reaches the client."):
            self.service.reschedule(actor_for(self.owner), self.piece_id, when=MOVED, reason="Tarde demais")

    def test_a_scheduled_piece_cannot_be_moved_by_its_planned_date(self):
        # The rule is copied into the piece when it is created (PD-43), so change the piece itself.
        ContentItem.objects.filter(pk=self.piece_id).update(client_approval_required=False)
        self._move_to_internal_review()
        self.service.decide_internal(actor_for(self.owner), self.piece_id, approve=True)
        self.service.schedule(actor_for(self.owner), self.piece_id, when=MOVED)

        with self.assertRaises(DomainError):
            self.service.reschedule(actor_for(self.owner), self.piece_id, when=MOVED, reason="Motivo")

    def test_a_client_cannot_change_the_planned_date(self):
        reviewer = make_membership(self.agency, Role.CLIENT)
        self.client.force_login(reviewer.user)

        response = self.client.post(
            reverse("content_reschedule", args=[self.piece_id]),
            {"planned_for": "2030-03-12T14:30", "reason": "Motivo"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(ContentItem.objects.get(pk=self.piece_id).planned_for, PLANNED)

    def test_another_organization_cannot_change_the_planned_date(self):
        other = make_organization("Outra agência")
        intruder = make_owner(other)
        self.client.force_login(intruder.user)

        response = self.client.post(
            reverse("content_reschedule", args=[self.piece_id]),
            {"planned_for": "2030-03-12T14:30", "reason": "Motivo"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(ContentItem.objects.get(pk=self.piece_id).planned_for, PLANNED)


class PlannedDateScreenTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.client_record = Client.objects.create(
            organization=self.agency, name="Padaria", client_approval_required=True
        )
        self.service = build_content_service()
        self.piece_id = self.service.create(
            actor_for(self.owner),
            client_id=self.client_record.pk,
            title="Post planejado",
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="Legenda"),
        )
        self.service.reschedule(actor_for(self.owner), self.piece_id, when=PLANNED, reason="Plano do mês")
        self.client.force_login(self.owner.user)

    def test_the_detail_page_offers_the_planned_date_form_while_open(self):
        response = self.client.get(reverse("content_detail", args=[self.piece_id]))

        self.assertContains(response, "Change planned date")
        self.assertContains(response, reverse("content_reschedule", args=[self.piece_id]))

    def test_the_detail_page_locks_the_planned_date_after_client_review(self):
        actor = actor_for(self.owner)
        self.service.move_to(actor, self.piece_id, ContentState.PLANNED)
        self.service.move_to(actor, self.piece_id, ContentState.IN_PRODUCTION)
        self.service.move_to(actor, self.piece_id, ContentState.INTERNAL_REVIEW)
        self.service.decide_internal(actor, self.piece_id, approve=True)

        response = self.client.get(reverse("content_detail", args=[self.piece_id]))

        self.assertNotContains(response, "Change planned date")
        self.assertContains(response, "is locked once the piece reaches the client")

    def test_the_calendar_shows_planned_pieces_on_their_day(self):
        response = self.client.get(reverse("content_calendar"), {"month": "2030-03"})

        self.assertContains(response, "Post planejado")
        self.assertContains(response, 'data-date="2030-03-10"')
        self.assertContains(response, 'draggable="true"')
        self.assertContains(response, "Planned:")

    def test_a_scheduled_piece_is_shown_but_not_draggable(self):
        ContentItem.objects.filter(pk=self.piece_id).update(client_approval_required=False)
        actor = actor_for(self.owner)
        self.service.move_to(actor, self.piece_id, ContentState.PLANNED)
        self.service.move_to(actor, self.piece_id, ContentState.IN_PRODUCTION)
        self.service.move_to(actor, self.piece_id, ContentState.INTERNAL_REVIEW)
        self.service.decide_internal(actor, self.piece_id, approve=True)
        self.service.schedule(actor, self.piece_id, when=MOVED)

        response = self.client.get(reverse("content_calendar"), {"month": "2030-03"})

        self.assertContains(response, "Post planejado")
        # The page script mentions draggable="true" too, so check for a draggable piece's id instead.
        self.assertNotContains(response, f'data-content-id="{self.piece_id}"')
