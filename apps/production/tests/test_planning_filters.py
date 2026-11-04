"""Calendar and board filters: client, channel, owner and state (CAL-001, NAV-014)."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.actors import actor_for
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.composition import build_content_service
from apps.production.domain.content import Channel, ContentFormat, VersionData
from apps.production.domain.states import ContentState
from apps.production.models import ContentItem


class PlanningFilterTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.ana = make_membership(self.agency, Role.CREATIVE, username="ana")
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria", client_approval_required=False)
        self.service = build_content_service()
        self.in_month = timezone.localdate().replace(day=1) + timedelta(days=3)
        self.instagram_by_owner = self.piece("Post A", Channel.INSTAGRAM, self.owner)
        self.linkedin_by_ana = self.piece("Post B", Channel.TIKTOK, self.ana)

    def piece(self, title, channel, owner):
        content_id = self.service.create(
            actor_for(self.owner),
            client_id=self.bakery.pk,
            title=title,
            channel=channel.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="x"),
        )
        item = ContentItem.objects.get(pk=content_id)
        ContentItem.objects.filter(pk=item.pk).update(owner=owner.user)
        return ContentItem.objects.get(pk=item.pk)

    def titles_on_board(self, params):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("content_board"), params)
        return {item.title for column in response.context["columns"] for item in column[1]}

    def test_board_filters_by_channel(self):
        self.assertEqual(self.titles_on_board({"channel": Channel.TIKTOK.value}), {"Post B"})

    def test_board_filters_by_owner(self):
        self.assertEqual(self.titles_on_board({"owner": self.owner.user.pk}), {"Post A"})

    def test_board_without_filters_shows_everything(self):
        self.assertEqual(self.titles_on_board({}), {"Post A", "Post B"})

    def test_an_invalid_channel_is_ignored_rather_than_hiding_everything(self):
        self.assertEqual(self.titles_on_board({"channel": "not-a-channel"}), {"Post A", "Post B"})

    def test_owner_choices_are_members_of_this_organization_only(self):
        outsider = make_owner(make_organization("Outra"))
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("content_board"))
        choices = [pk for pk, _label in response.context["filters"].fields["owner"].choices if pk]
        self.assertIn(self.ana.user.pk, choices)
        self.assertNotIn(outsider.user.pk, choices)

    def test_calendar_filters_by_state_and_channel(self):
        self.client.force_login(self.owner.user)
        month = self.in_month.strftime("%Y-%m")
        ContentItem.objects.filter(pk=self.instagram_by_owner.pk).update(
            state=ContentState.SCHEDULED.value, scheduled_for=timezone.now() + timedelta(days=1)
        )
        ContentItem.objects.filter(pk=self.linkedin_by_ana.pk).update(
            state=ContentState.PUBLISHED.value, scheduled_for=timezone.now() + timedelta(days=2)
        )

        by_state = self.client.get(
            reverse("content_calendar"), {"month": month, "state": ContentState.SCHEDULED.value}
        )
        by_channel = self.client.get(reverse("content_calendar"), {"month": month, "channel": Channel.TIKTOK.value})

        self.assertEqual(self.calendar_titles(by_state), {"Post A"})
        self.assertEqual(self.calendar_titles(by_channel), {"Post B"})

    def calendar_titles(self, response):
        return {item.title for week in response.context["weeks"] for day in week for item in day["items"]}

    def test_state_filter_is_not_offered_on_the_board(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("content_board"))
        self.assertNotIn("state", response.context["filters"].fields)

    def test_the_filter_panel_opens_when_any_filter_is_set(self):
        self.client.force_login(self.owner.user)
        closed = self.client.get(reverse("content_board"))
        open_panel = self.client.get(reverse("content_board"), {"channel": Channel.TIKTOK.value})

        self.assertNotContains(closed, '<details class="filters card" open>')
        self.assertContains(open_panel, '<details class="filters card" open>')

    def test_a_client_outside_the_scope_cannot_be_filtered_for(self):
        other = Client.objects.create(organization=self.agency, name="Secreta", client_approval_required=False)
        self.piece_for_other = self.service.create(
            actor_for(self.owner),
            client_id=other.pk,
            title="Post secreto",
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="x"),
        )
        account_manager = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="bia")
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=account_manager)
        self.client.force_login(account_manager.user)

        response = self.client.get(reverse("content_board"), {"client": other.pk})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["filters"].cleaned_data.get("client"))
        self.assertNotContains(response, "Post secreto")
