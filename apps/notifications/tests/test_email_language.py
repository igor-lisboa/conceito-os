"""Notification emails use the recipient's chosen language (NTF-010, TD-48)."""

from django.core import mail
from django.test import TestCase

from apps.accounts.roles import Role
from apps.core.testing import make_membership, make_organization
from apps.notifications.adapters import DEFAULT_EMAIL_LANGUAGE, _send_email
from apps.notifications.models import Notification


class NotificationEmailLanguageTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.client_member = make_membership(self.agency, Role.CLIENT)

    def _notify(self, kind="client_review"):
        return Notification.objects.create(
            organization=self.agency,
            recipient=self.client_member.user,
            kind=kind,
            params={"title": "Post de maio", "client": "Padaria"},
            url="/portal/1/",
            event_key=f"event-{kind}",
        )

    def test_email_is_sent_in_the_language_the_client_chose(self):
        self.client_member.user.language = "en"
        self.client_member.user.save()

        _send_email(self._notify())

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("is waiting for your approval.", mail.outbox[0].body)
        self.assertIn("Padaria", mail.outbox[0].body)

    def test_email_is_sent_in_portuguese_when_the_client_chose_it(self):
        self.client_member.user.language = "pt-br"
        self.client_member.user.save()

        _send_email(self._notify())

        self.assertIn("está aguardando sua aprovação.", mail.outbox[0].body)
        self.assertIn("Conceito OS:", mail.outbox[0].subject)

    def test_email_falls_back_to_the_default_language_when_nothing_was_chosen(self):
        self.assertEqual(self.client_member.user.language, "")
        self.assertEqual(DEFAULT_EMAIL_LANGUAGE, "pt-br")

        _send_email(self._notify())

        self.assertIn("está aguardando sua aprovação.", mail.outbox[0].body)

    def test_the_active_language_of_the_request_does_not_change_the_email(self):
        from django.utils import translation

        self.client_member.user.language = "en"
        self.client_member.user.save()

        before = translation.get_language()
        with translation.override("pt-br"):
            _send_email(self._notify())

        self.assertIn("is waiting for your approval.", mail.outbox[0].body)
        self.assertEqual(translation.get_language(), before)
