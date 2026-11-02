"""When a planned date changes, the open tasks of that piece due on the old day follow it (CAL-003)."""

from datetime import datetime, timedelta

from django.template.loader import render_to_string
from django.test import TestCase
from django.utils import timezone, translation

from apps.accounts.emails import send_welcome_email
from apps.clients.models import Client
from apps.core.actors import actor_for
from apps.core.testing import make_membership, make_organization, make_owner
from apps.production.composition import build_content_service
from apps.production.domain.content import Channel, ContentFormat, VersionData
from apps.tasks.models import Task

FIRST = timezone.make_aware(datetime(2030, 3, 10, 9, 0))
MOVED = timezone.make_aware(datetime(2030, 3, 12, 9, 0))


class TaskFollowsPlannedDateTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.client_record = Client.objects.create(organization=self.agency, name="Padaria")
        self.service = build_content_service()
        self.piece_id = self.service.create(
            actor_for(self.owner),
            client_id=self.client_record.pk,
            title="Post de março",
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="Legenda"),
        )
        self.service.reschedule(actor_for(self.owner), self.piece_id, when=FIRST, reason="Plano")

    def _task(self, title, due, done=False, content_id=None):
        return Task.objects.create(
            organization=self.agency,
            content_id=self.piece_id if content_id is None else content_id,
            title=title,
            due_date=due,
            done_at=timezone.now() if done else None,
        )

    def test_an_open_task_due_on_the_old_day_moves_with_the_piece(self):
        task = self._task("Gravar", FIRST.date())

        self.service.reschedule(actor_for(self.owner), self.piece_id, when=MOVED, reason="Feriado")

        task.refresh_from_db()
        self.assertEqual(task.due_date, MOVED.date())

    def test_a_task_with_its_own_deadline_stays_where_it_is(self):
        own = self._task("Aprovar fornecedor", FIRST.date() + timedelta(days=1))

        self.service.reschedule(actor_for(self.owner), self.piece_id, when=MOVED, reason="Feriado")

        own.refresh_from_db()
        self.assertEqual(own.due_date, FIRST.date() + timedelta(days=1))

    def test_a_done_task_is_not_changed(self):
        done = self._task("Gravado", FIRST.date(), done=True)

        self.service.reschedule(actor_for(self.owner), self.piece_id, when=MOVED, reason="Feriado")

        done.refresh_from_db()
        self.assertEqual(done.due_date, FIRST.date())

    def test_a_task_of_another_piece_is_not_changed(self):
        other_piece = self.service.create(
            actor_for(self.owner),
            client_id=self.client_record.pk,
            title="Outro post",
            channel=Channel.INSTAGRAM.value,
            content_format=ContentFormat.FEED.value,
            version=VersionData(caption="Legenda"),
        )
        other = self._task("Outra tarefa", FIRST.date(), content_id=other_piece)

        self.service.reschedule(actor_for(self.owner), self.piece_id, when=MOVED, reason="Feriado")

        other.refresh_from_db()
        self.assertEqual(other.due_date, FIRST.date())

    def test_a_change_on_the_same_day_moves_nothing(self):
        task = self._task("Gravar", FIRST.date())

        self.service.reschedule(
            actor_for(self.owner), self.piece_id, when=FIRST.replace(hour=15), reason="Mesmo dia"
        )

        task.refresh_from_db()
        self.assertEqual(task.due_date, FIRST.date())


class WelcomeEmailLanguageTests(TestCase):
    def setUp(self):
        from django.core import mail

        self.mail = mail
        self.agency = make_organization()

    def _welcome_subject(self, language):
        with translation.override(language):
            return render_to_string("emails/welcome_subject.txt", {"user": None, "login_url": ""}).strip()

    def test_the_welcome_email_follows_the_language_the_person_chose(self):
        user = make_membership(self.agency, "client").user
        user.language = "en"
        user.save()

        send_welcome_email(user)

        self.assertEqual(self.mail.outbox[-1].subject, self._welcome_subject("en"))

    def test_the_welcome_email_defaults_to_portuguese_when_nothing_was_chosen(self):
        user = make_membership(self.agency, "client").user

        send_welcome_email(user)

        self.assertEqual(self.mail.outbox[-1].subject, self._welcome_subject("pt-br"))
