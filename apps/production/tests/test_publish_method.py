"""Every publication records how it happened: by hand for now (INT-010, states-events)."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.clients.models import Client
from apps.core.actors import actor_for
from apps.core.exceptions import DomainError
from apps.core.testing import make_organization, make_owner
from apps.production.composition import build_content_service
from apps.production.domain.content import PUBLISH_METHOD_MANUAL, Channel, ContentFormat, VersionData
from apps.production.domain.states import ContentState
from apps.production.models import ContentItem


class PublishMethodTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria", client_approval_required=False)
        self.service = build_content_service()
        content_id = self.service.create(
            actor_for(self.owner),
            client_id=self.bakery.pk,
            title="Pão",
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="x"),
        )
        self.piece = ContentItem.objects.get(pk=content_id)
        owner = actor_for(self.owner)
        self.service.move_to(owner, self.piece.pk, ContentState.PLANNED)
        self.service.move_to(owner, self.piece.pk, ContentState.IN_PRODUCTION)
        self.service.move_to(owner, self.piece.pk, ContentState.INTERNAL_REVIEW)
        self.service.decide_internal(owner, self.piece.pk, approve=True)
        self.service.schedule(owner, self.piece.pk, when=timezone.now() + timedelta(days=1))

    def test_marking_published_records_the_manual_method(self):
        self.service.mark_published(actor_for(self.owner), self.piece.pk, url="")

        self.assertEqual(ContentItem.objects.get(pk=self.piece.pk).publish_method, PUBLISH_METHOD_MANUAL)

    def test_the_method_survives_a_reload_from_the_database(self):
        self.service.mark_published(actor_for(self.owner), self.piece.pk, url="https://example.com/p/1")

        reloaded = self.service.repository.get(self.agency.pk, self.piece.pk)

        self.assertEqual(reloaded.publish_method, PUBLISH_METHOD_MANUAL)

    def test_an_unknown_method_is_refused(self):
        content = self.service.repository.get(self.agency.pk, self.piece.pk)
        with self.assertRaises(DomainError):
            content.mark_published(now=timezone.now(), method="api")

    def test_the_piece_page_says_it_was_published_by_hand(self):
        self.service.mark_published(actor_for(self.owner), self.piece.pk, url="")
        self.client.force_login(self.owner.user)

        response = self.client.get(reverse("content_detail", args=[self.piece.pk]))

        self.assertContains(response, "Marked as published by hand")
