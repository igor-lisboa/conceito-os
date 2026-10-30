"""The link of a post the team published by hand is kept (TD-43, INT-010)."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clients.models import Client
from core.actors import actor_for
from core.testing import make_organization, make_owner
from production.composition import build_content_service
from production.domain.content import Channel, ContentFormat, VersionData
from production.domain.states import ContentState
from production.models import ContentItem


class PublishedLinkTests(TestCase):
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

    def test_publishing_keeps_the_link_of_the_post(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("content_action", args=[self.piece.pk, "mark_published"]),
            {"link": "https://www.instagram.com/p/abc123/"},
        )

        self.piece.refresh_from_db()
        self.assertEqual(self.piece.state, ContentState.PUBLISHED.value)
        self.assertEqual(self.piece.published_url, "https://www.instagram.com/p/abc123/")
        self.assertContains(self.client.get(reverse("content_detail", args=[self.piece.pk])), "Published post")

    def test_the_link_is_optional(self):
        self.client.force_login(self.owner.user)
        self.client.post(reverse("content_action", args=[self.piece.pk, "mark_published"]), {})

        self.piece.refresh_from_db()
        self.assertEqual(self.piece.state, ContentState.PUBLISHED.value)
        self.assertEqual(self.piece.published_url, "")

    def test_a_malformed_link_is_refused_and_nothing_changes(self):
        self.client.force_login(self.owner.user)
        self.client.post(reverse("content_action", args=[self.piece.pk, "mark_published"]), {"link": "nope"})

        self.piece.refresh_from_db()
        self.assertEqual(self.piece.state, ContentState.SCHEDULED.value)
