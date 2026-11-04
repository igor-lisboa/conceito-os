"""Authors edit and delete their own comments (TD-S13, PROPOSAL pending the product owner)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.models import Comment

from .test_comments_and_planning import ContentFixtureMixin


class CommentEditDeleteTests(ContentFixtureMixin, TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)
        self.piece = self.make_piece(self.bakery, self.owner)
        self.comment = Comment.objects.create(
            organization=self.agency, content=self.piece, author=self.owner.user, body="Texto original"
        )

    def edit_url(self, comment=None):
        return reverse("content_comment_edit", args=[self.piece.pk, (comment or self.comment).pk])

    def delete_url(self, comment=None):
        return reverse("content_comment_delete", args=[self.piece.pk, (comment or self.comment).pk])

    def test_the_author_can_edit_the_comment_and_it_is_marked_edited(self):
        self.client.force_login(self.owner.user)

        response = self.client.post(self.edit_url(), {"body": "Texto corrigido"})

        self.assertRedirects(response, reverse("content_detail", args=[self.piece.pk]))
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "Texto corrigido")
        self.assertIsNotNone(self.comment.edited_at)

    def test_the_edit_page_shows_the_current_text(self):
        self.client.force_login(self.owner.user)

        response = self.client.get(self.edit_url())

        self.assertContains(response, "Texto original")

    def test_another_member_cannot_edit_the_comment(self):
        self.client.force_login(self.manager.user)

        self.assertEqual(self.client.get(self.edit_url()).status_code, 403)
        self.assertEqual(self.client.post(self.edit_url(), {"body": "Invasão"}).status_code, 403)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "Texto original")

    def test_another_member_cannot_delete_the_comment(self):
        self.client.force_login(self.manager.user)

        self.assertEqual(self.client.post(self.delete_url()).status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_the_author_can_delete_the_comment(self):
        self.client.force_login(self.owner.user)

        response = self.client.post(self.delete_url())

        self.assertRedirects(response, reverse("content_detail", args=[self.piece.pk]))
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_deleting_takes_a_post_only(self):
        self.client.force_login(self.owner.user)

        self.assertEqual(self.client.get(self.delete_url()).status_code, 405)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_an_empty_or_huge_edit_is_refused_and_nothing_changes(self):
        self.client.force_login(self.owner.user)

        self.assertEqual(self.client.post(self.edit_url(), {"body": "   "}).status_code, 400)
        self.assertEqual(self.client.post(self.edit_url(), {"body": "x" * 2001}).status_code, 400)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "Texto original")
        self.assertIsNone(self.comment.edited_at)

    def test_a_comment_on_a_piece_the_person_cannot_see_is_not_found(self):
        other_client = Client.objects.create(organization=self.agency, name="Outro cliente")
        hidden_piece = self.make_piece(other_client, self.owner, title="Oculto")
        hidden_comment = Comment.objects.create(
            organization=self.agency, content=hidden_piece, author=self.owner.user, body="Segredo"
        )
        self.client.force_login(self.manager.user)

        url = reverse("content_comment_edit", args=[hidden_piece.pk, hidden_comment.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_the_comment_must_belong_to_the_piece_in_the_url(self):
        other_piece = self.make_piece(self.bakery, self.owner, title="Outro post")
        self.client.force_login(self.owner.user)

        url = reverse("content_comment_edit", args=[other_piece.pk, self.comment.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_the_detail_page_offers_edit_and_delete_only_on_own_comments(self):
        Comment.objects.create(
            organization=self.agency, content=self.piece, author=self.manager.user, body="Da Ana"
        )
        self.client.force_login(self.owner.user)

        response = self.client.get(reverse("content_detail", args=[self.piece.pk]))

        self.assertContains(response, self.edit_url())
        self.assertContains(response, self.delete_url())
        self.assertEqual(response.content.decode().count(self.delete_url()), 1)
