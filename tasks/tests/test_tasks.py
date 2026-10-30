"""Tasks: follow-ups for a client or a piece (TD-06)."""

from django.test import TestCase
from django.urls import reverse

from accounts.roles import Role
from clients.models import Client, ClientAccess
from core.testing import make_membership, make_organization, make_owner
from tasks.models import Task


class TaskTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.clinic = Client.objects.create(organization=self.agency, name="Clínica")
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)
        self.bakery_task = Task.objects.create(organization=self.agency, client=self.bakery, title="Cobrar fotos")
        self.clinic_task = Task.objects.create(organization=self.agency, client=self.clinic, title="Enviar contrato")
        self.agency_task = Task.objects.create(organization=self.agency, title="Revisar preços")

    def titles_for(self, user):
        self.client.force_login(user)
        return {task.title for task in self.client.get(reverse("task_list")).context["tasks"]}

    def test_owner_sees_every_task_of_the_organization(self):
        self.assertEqual(self.titles_for(self.owner.user), {"Cobrar fotos", "Enviar contrato", "Revisar preços"})

    def test_manager_sees_their_brands_and_the_agency_tasks(self):
        self.assertEqual(self.titles_for(self.manager.user), {"Cobrar fotos", "Revisar preços"})

    def test_creative_without_access_sees_no_brand_tasks(self):
        creative = make_membership(self.agency, Role.CREATIVE)
        self.assertEqual(self.titles_for(creative.user), set())

    def test_mine_filter_shows_only_tasks_owned_by_me(self):
        self.bakery_task.owner = self.manager.user
        self.bakery_task.save()
        self.client.force_login(self.manager.user)
        tasks = self.client.get(reverse("task_list"), {"mine": "1"}).context["tasks"]
        self.assertEqual([task.title for task in tasks], ["Cobrar fotos"])

    def test_creating_a_task_for_a_brand_in_scope(self):
        self.client.force_login(self.manager.user)
        self.client.post(
            reverse("task_create"),
            {"title": "Pedir aprovação", "client": self.bakery.pk, "due_date": "2026-12-01"},
        )
        task = Task.objects.get(title="Pedir aprovação")
        self.assertEqual(task.organization, self.agency)
        self.assertEqual(task.created_by, self.manager.user)

    def test_a_task_for_a_brand_out_of_scope_is_refused(self):
        self.client.force_login(self.manager.user)
        self.client.post(reverse("task_create"), {"title": "Invasão", "client": self.clinic.pk})
        self.assertFalse(Task.objects.filter(title="Invasão").exists())

    def test_marking_a_task_done_and_back(self):
        self.client.force_login(self.owner.user)
        self.client.post(reverse("task_toggle", args=[self.bakery_task.pk]))
        self.bakery_task.refresh_from_db()
        self.assertTrue(self.bakery_task.is_done)

        self.client.post(reverse("task_toggle", args=[self.bakery_task.pk]))
        self.bakery_task.refresh_from_db()
        self.assertFalse(self.bakery_task.is_done)

    def test_a_task_outside_scope_cannot_be_toggled(self):
        self.client.force_login(self.manager.user)
        response = self.client.post(reverse("task_toggle", args=[self.clinic_task.pk]))
        self.assertEqual(response.status_code, 404)
        self.clinic_task.refresh_from_db()
        self.assertFalse(self.clinic_task.is_done)
