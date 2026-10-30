"""The Django adapter: saving and loading the Content aggregate through real tables."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts.roles import Role
from apps.clients.models import Client
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.adapters.django_repository import DjangoContentRepository
from apps.production.domain.content import Channel, Content, ContentFormat, VersionData
from apps.production.domain.states import ContentState
from apps.production.models import Approval as ApprovalRow
from apps.production.models import ContentItem, ContentVersion


class DjangoContentRepositoryTests(TestCase):
    def setUp(self):
        self.organization = make_organization()
        self.owner = make_owner(self.organization)
        self.client_record = Client.objects.create(organization=self.organization, name="Padaria")
        self.repository = DjangoContentRepository()

    def new_content(self):
        return Content.create(
            organization_id=self.organization.pk,
            client_id=self.client_record.pk,
            owner_id=self.owner.user_id,
            title="Carrossel de sexta",
            channel=Channel.INSTAGRAM,
            content_format=ContentFormat.CAROUSEL,
            client_approval_required=True,
            first_version=VersionData(caption="Legenda", cta="Peça já", media_url="https://example.com/a.jpg"),
            created_by_user_id=self.owner.user_id,
        )

    def test_saved_content_loads_back_with_the_same_values(self):
        content = self.new_content()
        self.repository.save(content)

        loaded = self.repository.get(self.organization.pk, content.id)

        self.assertEqual(loaded.title, "Carrossel de sexta")
        self.assertEqual(loaded.channel, Channel.INSTAGRAM)
        self.assertEqual(loaded.content_format, ContentFormat.CAROUSEL)
        self.assertEqual(loaded.state, ContentState.DRAFT)
        self.assertEqual(loaded.latest_version.data.cta, "Peça já")
        self.assertEqual(loaded.latest_version.data.media_url, "https://example.com/a.jpg")

    def test_get_respects_the_organization_boundary(self):
        content = self.new_content()
        self.repository.save(content)
        other_agency = make_organization("Outra agência")

        self.assertIsNone(self.repository.get(other_agency.pk, content.id))

    def test_only_new_versions_and_approvals_are_inserted_on_each_save(self):
        content = self.new_content()
        self.repository.save(content)

        content.move_to(ContentState.PLANNED)
        content.move_to(ContentState.IN_PRODUCTION)
        content.move_to(ContentState.INTERNAL_REVIEW)
        content.add_version(VersionData(caption="Legenda 2"), created_by_user_id=self.owner.user_id)
        content.decide_internal(approve=True, comment="", actor_user_id=self.owner.user_id)
        self.repository.save(content)
        self.repository.save(content)  # saving again must not duplicate rows

        row = ContentItem.objects.get(pk=content.id)
        self.assertEqual(row.versions.count(), 2)
        self.assertEqual(ContentVersion.objects.filter(content=row).count(), 2)
        self.assertEqual(ApprovalRow.objects.filter(content=row).count(), 1)
        self.assertEqual(row.state, ContentState.CLIENT_REVIEW.value)

    def test_approval_keeps_its_link_to_the_version_it_reviewed(self):
        content = self.new_content()
        self.repository.save(content)
        content.move_to(ContentState.PLANNED)
        content.move_to(ContentState.IN_PRODUCTION)
        content.move_to(ContentState.INTERNAL_REVIEW)
        content.decide_internal(approve=True, comment="", actor_user_id=self.owner.user_id)
        self.repository.save(content)

        loaded = self.repository.get(self.organization.pk, content.id)

        self.assertEqual(loaded.approvals[0].version_number, 1)
        self.assertEqual(loaded.approvals[0].actor_user_id, self.owner.user_id)

    def test_scheduled_date_and_failure_reason_survive_a_round_trip(self):
        content = self.new_content()
        self.repository.save(content)
        for target in (ContentState.PLANNED, ContentState.IN_PRODUCTION, ContentState.INTERNAL_REVIEW):
            content.move_to(target)
        content.decide_internal(approve=True, comment="", actor_user_id=self.owner.user_id)
        content.decide_client(approve=True, comment="", actor_user_id=self.owner.user_id)
        now = timezone.now()
        content.schedule(now + timedelta(days=2), now=now)
        content.mark_failed("Token expirado")
        self.repository.save(content)

        loaded = self.repository.get(self.organization.pk, content.id)

        self.assertEqual(loaded.state, ContentState.FAILED)
        self.assertEqual(loaded.failure_reason, "Token expirado")
        self.assertIsNotNone(loaded.scheduled_for)

    def test_client_approval_rule_and_membership_lookups(self):
        self.assertTrue(self.repository.client_approval_rule(self.organization.pk, self.client_record.pk))
        self.assertIsNone(self.repository.client_approval_rule(self.organization.pk, 999999))

        self.assertTrue(self.repository.is_internal_member(self.organization.pk, self.owner.user_id))
        client_user = make_membership(self.organization, Role.CLIENT)
        self.assertFalse(self.repository.is_internal_member(self.organization.pk, client_user.user_id))
