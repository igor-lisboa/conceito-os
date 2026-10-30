"""Comments and mentions (TD-29), calendar and board (TD-04, TD-05), and duplicating a piece (CAL-004)."""

from datetime import timedelta

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.roles import Role
from clients.models import Client, ClientAccess
from core.actors import actor_for
from core.testing import make_membership, make_organization, make_owner
from notifications.models import Notification
from production.comments import mentioned_emails
from production.composition import build_content_service
from production.domain.content import Channel, ContentFormat, VersionData
from production.domain.states import ContentState
from production.models import Comment, ContentItem


class ContentFixtureMixin:
    def make_piece(self, client_record, owner_membership, title="Post", scheduled_in=None):
        service = build_content_service()
        content_id = service.create(
            actor_for(owner_membership),
            client_id=client_record.pk,
            title=title,
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="Legenda", cta="Peça já", script="Roteiro"),
        )
        piece = ContentItem.objects.get(pk=content_id)
        if scheduled_in is not None:
            actor = actor_for(owner_membership)
            service.move_to(actor, piece.pk, ContentState.PLANNED)
            service.move_to(actor, piece.pk, ContentState.IN_PRODUCTION)
            service.move_to(actor, piece.pk, ContentState.INTERNAL_REVIEW)
            service.decide_internal(actor, piece.pk, approve=True)
            if client_record.client_approval_required:
                reviewer = make_membership(client_record.organization, Role.CLIENT)
                ClientAccess.objects.create(
                    organization=client_record.organization, client=client_record, membership=reviewer
                )
                service.decide_client(actor_for(reviewer), piece.pk, approve=True)
            service.schedule(actor, piece.pk, when=scheduled_in)
            piece.refresh_from_db()
        return piece


class MentionParsingTests(TestCase):
    def test_finds_email_addresses_after_an_at_sign(self):
        self.assertEqual(
            mentioned_emails("Oi @Ana@agencia.com.br, veja isto com @bruno@agencia.com.br."),
            {"ana@agencia.com.br", "bruno@agencia.com.br"},
        )

    def test_plain_text_mentions_nothing(self):
        self.assertEqual(mentioned_emails("sem menções aqui"), set())


class CommentTests(ContentFixtureMixin, TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)
        self.piece = self.make_piece(self.bakery, self.owner)

    def comment(self, user, body):
        self.client.force_login(user)
        return self.client.post(reverse("content_comment", args=[self.piece.pk]), {"body": body})

    def test_comment_is_saved_on_the_piece(self):
        self.comment(self.owner.user, "Ficou ótimo")
        self.assertEqual(Comment.objects.get().body, "Ficou ótimo")

    def test_mentioned_member_is_notified_with_a_link_to_the_piece(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.comment(self.owner.user, f"@{self.manager.user.email} confere isto")

        note = Notification.objects.get(recipient=self.manager.user)
        self.assertEqual(note.kind, "mention")
        self.assertEqual(note.url, f"/conteudos/{self.piece.pk}/")
        self.assertEqual(len(mail.outbox), 1)

    def test_mention_of_someone_outside_the_organization_notifies_nobody(self):
        outsider = make_owner(make_organization("Outra"))
        self.comment(self.owner.user, f"@{outsider.user.email} olha")
        self.assertFalse(Notification.objects.filter(recipient=outsider.user).exists())

    def test_people_do_not_notify_themselves(self):
        self.comment(self.owner.user, f"@{self.owner.user.email} lembrete")
        self.assertFalse(Notification.objects.filter(recipient=self.owner.user).exists())

    def test_empty_or_huge_comment_is_refused(self):
        self.comment(self.owner.user, "   ")
        self.comment(self.owner.user, "x" * 2001)
        self.assertFalse(Comment.objects.exists())

    def test_someone_without_access_cannot_comment(self):
        outsider = make_membership(self.agency, Role.CREATIVE)
        response = self.comment(outsider.user, "entrei")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Comment.objects.exists())


class PortalCommentPrivacyTests(ContentFixtureMixin, TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.portal_user = make_membership(self.agency, Role.CLIENT)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.portal_user)
        self.piece = self.make_piece(self.bakery, self.owner)
        Comment.objects.create(
            organization=self.agency, content=self.piece, author=self.owner.user, body="NOTA-INTERNA"
        )

    def test_client_sees_their_own_comments_but_not_internal_notes(self):
        self.client.force_login(self.portal_user.user)
        self.client.post(reverse("portal_comment", args=[self.piece.pk]), {"body": "Pode trocar a cor?"})

        page = self.client.get(reverse("portal_detail", args=[self.piece.pk]))

        self.assertContains(page, "Pode trocar a cor?")
        self.assertNotContains(page, "NOTA-INTERNA")


class CalendarAndBoardTests(ContentFixtureMixin, TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria", client_approval_required=False)
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)
        self.future = timezone.now() + timedelta(days=3)
        self.scheduled = self.make_piece(self.bakery, self.owner, title="Agendado", scheduled_in=self.future)
        self.draft = self.make_piece(self.bakery, self.owner, title="Rascunho")

    def test_calendar_shows_the_scheduled_piece_in_its_month(self):
        self.client.force_login(self.owner.user)
        month = timezone.localdate(self.future).strftime("%Y-%m")
        response = self.client.get(reverse("content_calendar"), {"month": month})
        self.assertContains(response, "Agendado")
        self.assertNotContains(response, "Rascunho")

    def test_calendar_month_without_pieces_is_empty(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("content_calendar"), {"month": "1999-01"})
        self.assertContains(response, "Nothing scheduled this month.")

    def test_calendar_respects_visibility(self):
        other = Client.objects.create(organization=self.agency, name="Clínica")
        self.make_piece(other, self.owner, title="Clínica secreta", scheduled_in=self.future)
        self.client.force_login(self.manager.user)
        month = timezone.localdate(self.future).strftime("%Y-%m")
        response = self.client.get(reverse("content_calendar"), {"month": month})
        self.assertContains(response, "Agendado")
        self.assertNotContains(response, "Clínica secreta")

    def test_board_has_one_column_per_stage_and_places_cards(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("content_board"))
        columns = dict((state.value, items) for state, items in response.context["columns"])
        self.assertEqual([item.title for item in columns["draft"]], ["Rascunho"])
        self.assertEqual([item.title for item in columns["scheduled"]], ["Agendado"])
        self.assertEqual(len(columns), len(ContentState))


class DuplicateTests(ContentFixtureMixin, TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.piece = self.make_piece(self.bakery, self.owner, title="Pão de queijo")

    def test_duplicate_is_a_new_draft_with_the_latest_text(self):
        self.client.force_login(self.owner.user)
        response = self.client.post(reverse("content_duplicate", args=[self.piece.pk]))

        copy = ContentItem.objects.exclude(pk=self.piece.pk).get()
        self.assertEqual(copy.state, ContentState.DRAFT.value)
        self.assertTrue(copy.title.startswith("Pão de queijo ("))
        self.assertEqual(copy.versions.order_by("-number").first().caption, "Legenda")
        self.assertRedirects(response, reverse("content_detail", args=[copy.pk]))

    def test_duplicating_a_piece_out_of_scope_is_not_found(self):
        outsider = make_membership(self.agency, Role.CREATIVE)
        self.client.force_login(outsider.user)
        response = self.client.post(reverse("content_duplicate", args=[self.piece.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(ContentItem.objects.count(), 1)
