import uuid

from django.test import TestCase
from django.urls import reverse

from accounts.roles import Role
from core.testing import make_membership, make_organization, make_owner
from notifications.models import Notification

CONTENT_ID = uuid.UUID("6f1c2a4e-9b3d-4e8f-8a7c-1d2e3f4a5b6c")


class NotificationInboxTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.user = self.owner.user
        self.note = Notification.objects.create(
            organization=self.agency,
            recipient=self.user,
            kind="internal_review",
            params={"title": "Post", "client": "Padaria"},
            url=f"/conteudos/{CONTENT_ID}/",
            event_key="e1",
        )

    def test_inbox_lists_my_notifications_with_the_translated_message(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("notification_list"))
        self.assertContains(response, "“Post” for Padaria is ready for internal review.")

    def test_others_notifications_are_not_listed(self):
        stranger = make_membership(self.agency, Role.CREATIVE)
        self.client.force_login(stranger.user)
        response = self.client.get(reverse("notification_list"))
        self.assertNotContains(response, "is ready for internal review")

    def test_opening_a_notification_marks_it_read_and_goes_to_the_item(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("notification_open", args=[self.note.pk]))

        self.assertRedirects(response, f"/conteudos/{CONTENT_ID}/", fetch_redirect_response=False)
        self.note.refresh_from_db()
        self.assertFalse(self.note.is_unread)

    def test_someone_else_cannot_open_my_notification(self):
        stranger = make_membership(self.agency, Role.CREATIVE)
        self.client.force_login(stranger.user)
        response = self.client.get(reverse("notification_open", args=[self.note.pk]))
        self.assertEqual(response.status_code, 404)

    def test_mark_all_as_read(self):
        self.client.force_login(self.user)
        self.client.post(reverse("notification_read_all"))
        self.assertFalse(Notification.objects.filter(recipient=self.user, read_at__isnull=True).exists())

    def test_navigation_shows_the_unread_count(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Notifications (1)")
