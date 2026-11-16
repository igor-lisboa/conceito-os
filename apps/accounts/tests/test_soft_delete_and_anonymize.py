"""Soft delete always, and anonymization instead of deletion (DAT-007, DAT-011, D-17).

Decided 2026-11-16: keep everything forever; anonymize personal data on request.
"""

from django.test import TestCase
from django.urls import reverse

from apps.accounts import team
from apps.accounts.models import Membership, MFADevice
from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.audit import AuditEvent
from apps.core.exceptions import DomainError, Forbidden
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.models import Comment, ContentItem


class SoftDeleteTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)

    def test_removing_a_member_keeps_the_row_and_hides_it(self):
        team.remove_member(self.owner, self.manager)

        self.assertFalse(Membership.objects.filter(pk=self.manager.pk).exists())
        removed = Membership.all_objects.get(pk=self.manager.pk)
        self.assertIsNotNone(removed.deleted_at)
        self.assertEqual(ClientAccess.all_objects.filter(membership=self.manager).count(), 1)
        self.assertFalse(ClientAccess.objects.filter(membership=self.manager).exists())

    def test_reinviting_a_removed_person_restores_the_same_membership(self):
        team.remove_member(self.owner, self.manager)

        restored = team.invite_member(
            self.owner, email=self.manager.user.email, role=Role.CREATIVE, client_ids=[self.bakery.pk]
        )

        self.assertEqual(restored.pk, self.manager.pk)
        self.assertIsNone(restored.deleted_at)
        self.assertEqual(restored.role, Role.CREATIVE.value)
        self.assertEqual(Membership.all_objects.filter(user=self.manager.user).count(), 1)
        self.assertTrue(ClientAccess.objects.filter(membership=restored, client=self.bakery).exists())

    def test_deleting_a_comment_keeps_the_row(self):
        piece = ContentItem.objects.create(
            organization=self.agency, client=self.bakery, title="Post", channel="instagram",
            content_format="feed", state="draft",
        )
        comment = Comment.objects.create(
            organization=self.agency, content=piece, author=self.owner.user, body="Ola"
        )

        comment.delete()

        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
        self.assertIsNotNone(Comment.all_objects.get(pk=comment.pk).deleted_at)

    def test_a_bulk_delete_is_soft_too(self):
        ClientAccess.objects.filter(membership=self.manager).delete()

        self.assertEqual(ClientAccess.all_objects.filter(membership=self.manager).count(), 1)
        self.assertFalse(ClientAccess.objects.filter(membership=self.manager).exists())


class AnonymizeTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.person = make_membership(self.agency, Role.CREATIVE, username="bia")
        self.person.user.first_name = "Beatriz"
        self.person.user.last_name = "Souza"
        self.person.user.save()
        self.original_email = self.person.user.email
        MFADevice.objects.create(user=self.person.user, secret="JBSWY3DPEHPK3PXP", confirmed=True)

    def anonymize(self):
        return team.anonymize_member(self.owner, self.person)

    def test_an_active_person_cannot_be_anonymized(self):
        with self.assertRaises(DomainError):
            self.anonymize()

        self.person.user.refresh_from_db()
        self.assertEqual(self.person.user.email, self.original_email)

    def test_a_removed_person_is_anonymized_and_the_records_stay(self):
        piece = ContentItem.objects.create(
            organization=self.agency, client=self.bakery, title="Post", channel="instagram",
            content_format="feed", state="draft",
        )
        Comment.objects.create(organization=self.agency, content=piece, author=self.person.user, body="Oi")
        team.remove_member(self.owner, self.person)

        self.anonymize()

        self.person.user.refresh_from_db()
        self.assertTrue(self.person.user.email.endswith("@anonymized.invalid"))
        self.assertNotIn("bia", self.person.user.username)
        self.assertEqual(self.person.user.first_name, "")
        self.assertEqual(self.person.user.last_name, "")
        self.assertFalse(self.person.user.is_active)
        self.assertFalse(self.person.user.has_usable_password())
        self.assertFalse(MFADevice.objects.get(user=self.person.user).confirmed)
        comment = Comment.objects.get(body="Oi")
        self.assertEqual(comment.author_id, self.person.user.pk)

    def test_the_audit_trail_records_it_without_the_old_email(self):
        team.remove_member(self.owner, self.person)

        self.anonymize()

        event = AuditEvent.objects.get(action=team.MEMBER_ANONYMIZED)
        self.assertNotIn(self.original_email, str(event.metadata))

    def test_anonymizing_twice_does_nothing_new(self):
        team.remove_member(self.owner, self.person)
        self.anonymize()
        self.anonymize()

        self.assertEqual(AuditEvent.objects.filter(action=team.MEMBER_ANONYMIZED).count(), 1)

    def test_the_anonymized_person_cannot_sign_in(self):
        team.remove_member(self.owner, self.person)
        self.anonymize()

        self.assertFalse(self.client.login(username=self.original_email, password="senha-de-teste-123"))

    def test_an_account_manager_cannot_anonymize(self):
        team.remove_member(self.owner, self.person)
        manager = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")
        with self.assertRaises(Forbidden):
            team.anonymize_member(manager, self.person)

    def test_the_owner_anonymizes_from_the_team_page(self):
        team.remove_member(self.owner, self.person)
        self.client.force_login(self.owner.user)

        page = self.client.get(reverse("team_list"))
        self.assertContains(page, "Removed people")

        self.client.post(reverse("team_anonymize", args=[self.person.pk]))
        self.person.user.refresh_from_db()
        self.assertTrue(self.person.user.email.endswith("@anonymized.invalid"))

    def test_an_active_person_cannot_be_anonymized_from_the_page(self):
        self.client.force_login(self.owner.user)

        self.client.post(reverse("team_anonymize", args=[self.person.pk]))

        self.person.user.refresh_from_db()
        self.assertEqual(self.person.user.email, self.original_email)
