"""Every record is identified by a GUID (UUID), and numbers in URLs are refused."""

from django.apps import apps
from django.db import models
from django.test import TestCase
from django.urls import reverse

from accounts.roles import Role
from core.testing import make_membership, make_organization, make_owner


class PrimaryKeyTests(TestCase):
    def test_every_model_of_this_project_uses_a_uuid_primary_key(self):
        project_apps = ("accounts", "clients", "core", "production", "notifications", "crm", "reports", "tasks")
        offenders = [
            model._meta.label
            for model in apps.get_models()
            if model._meta.app_label in project_apps
            and not isinstance(model._meta.pk, models.UUIDField)
        ]
        self.assertEqual(offenders, [], "these models still use a numeric primary key")

    def test_a_numeric_id_in_the_url_does_not_find_anything(self):
        agency = make_organization()
        owner = make_owner(agency)
        self.client.force_login(owner.user)

        response = self.client.get("/clientes/12/")

        self.assertEqual(response.status_code, 404)

    def test_a_guid_in_the_url_works(self):
        agency = make_organization()
        owner = make_owner(agency)
        self.client.force_login(owner.user)
        from clients.models import Client

        client_record = Client.objects.create(organization=agency, name="Padaria")
        response = self.client.get(reverse("client_detail", args=[client_record.pk]))
        self.assertEqual(response.status_code, 200)

    def test_people_get_guids_too(self):
        creative = make_membership(make_organization(), Role.CREATIVE)
        self.assertEqual(type(creative.user.pk).__name__, "UUID")
