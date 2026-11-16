"""Mentions reach only internal people who can open the piece (D-31, NTF-006, PRO-004).

Decided 2026-11-16: option A for D-31 (only people who can see the piece), and option B for
the edit question in D-30 (a person mentioned for the first time by an edit is notified).
"""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner
from apps.notifications.models import Notification
from apps.production.comments import add_comment, update_comment
from apps.production.models import ContentItem


class MentionVisibilityTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.shop = Client.objects.create(organization=self.agency, name="Loja")

        self.manager_bakery = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager_bakery)

        self.manager_shop = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="bia")
        ClientAccess.objects.create(organization=self.agency, client=self.shop, membership=self.manager_shop)

        self.client_user = make_membership(self.agency, Role.CLIENT, username="cliente")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.client_user)

        self.piece = self.create_piece()

    def create_piece(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("content_create"),
            {
                "client": self.bakery.pk,
                "title": "Post da semana",
                "channel": "instagram",
                "content_format": "feed",
                "caption": "Legenda",
            },
        )
        return ContentItem.objects.get(title="Post da semana")

    def mentions_received_by(self, membership):
        return Notification.objects.filter(recipient=membership.user, kind="mention").count()

    def test_an_internal_member_with_access_is_notified(self):
        add_comment(self.piece, self.owner.user, "Olhem isto @ana@example.com")

        self.assertEqual(self.mentions_received_by(self.manager_bakery), 1)

    def test_an_internal_member_without_access_to_the_client_is_not_notified(self):
        add_comment(self.piece, self.owner.user, "Ver com @bia@example.com")

        self.assertEqual(self.mentions_received_by(self.manager_shop), 0)

    def test_a_client_member_is_never_notified_even_with_access_to_the_brand(self):
        add_comment(self.piece, self.owner.user, "Interno: @cliente@example.com")

        self.assertEqual(self.mentions_received_by(self.client_user), 0)

    def test_the_author_is_not_notified_of_their_own_mention(self):
        add_comment(self.piece, self.manager_bakery.user, "Eu mesmo @ana@example.com")

        self.assertEqual(self.mentions_received_by(self.manager_bakery), 0)

    def test_an_edit_notifies_a_person_mentioned_for_the_first_time(self):
        comment = add_comment(self.piece, self.owner.user, "Primeira versao")
        self.assertEqual(self.mentions_received_by(self.manager_bakery), 0)

        update_comment(comment, "Primeira versao, agora com @ana@example.com")

        self.assertEqual(self.mentions_received_by(self.manager_bakery), 1)

    def test_an_edit_does_not_notify_someone_already_mentioned(self):
        comment = add_comment(self.piece, self.owner.user, "Olha @ana@example.com")
        self.assertEqual(self.mentions_received_by(self.manager_bakery), 1)

        update_comment(comment, "Olha @ana@example.com, texto corrigido")

        self.assertEqual(self.mentions_received_by(self.manager_bakery), 1)

    def test_an_edit_that_mentions_a_hidden_person_notifies_nobody_hidden(self):
        comment = add_comment(self.piece, self.owner.user, "Sem mencao")

        update_comment(comment, "Agora @bia@example.com")

        self.assertEqual(self.mentions_received_by(self.manager_shop), 0)
