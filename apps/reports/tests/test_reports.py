"""Monthly report with manual metrics (TD-01 manual part, MET-003: missing shows as N/D)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Client, ClientAccess
from apps.core.testing import make_membership, make_organization, make_owner
from apps.reports.models import MetricEntry


class MonthlyReportTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)

    def enter(self, user, **data):
        self.client.force_login(user)
        payload = {
            "client": self.bakery.pk,
            "platform": "instagram",
            "metric": "reach",
            "month": "2026-10",
            "value": "1500",
        }
        payload.update(data)
        return self.client.post(reverse("metric_entry"), payload)

    def test_entered_values_appear_and_missing_ones_show_as_nd(self):
        self.enter(self.owner.user)
        response = self.client.get(reverse("report"), {"client": self.bakery.pk, "month": "2026-10"})

        rows = {(row["platform"], row["metric"]): row for row in response.context["rows"]}
        self.assertEqual(rows[("Instagram", "Reach")]["value"], 1500)
        self.assertFalse(rows[("Instagram", "Reach")]["missing"])
        self.assertEqual(rows[("Instagram", "Saves")]["value"], "N/D")
        self.assertTrue(rows[("Instagram", "Saves")]["missing"])

    def test_entering_the_same_month_updates_the_value(self):
        self.enter(self.owner.user, value="1500")
        self.enter(self.owner.user, value="1800")

        self.assertEqual(MetricEntry.objects.filter(client=self.bakery).count(), 1)
        self.assertEqual(MetricEntry.objects.get(client=self.bakery).value, 1800)

    def test_the_entry_records_source_manual_and_who_entered_it(self):
        self.enter(self.manager.user)
        entry = MetricEntry.objects.get(client=self.bakery)
        self.assertEqual(entry.source, "manual")
        self.assertEqual(entry.created_by, self.manager.user)

    def test_a_month_that_is_not_in_the_format_is_refused(self):
        response = self.enter(self.owner.user, month="outubro")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(MetricEntry.objects.exists())

    def test_a_negative_value_is_refused(self):
        self.enter(self.owner.user, value="-5")
        self.assertFalse(MetricEntry.objects.exists())

    def test_a_client_user_cannot_enter_values(self):
        portal_user = make_membership(self.agency, Role.CLIENT)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=portal_user)
        self.enter(portal_user.user)
        self.assertFalse(MetricEntry.objects.exists())

    def test_a_client_outside_the_user_scope_is_not_offered(self):
        other_client = Client.objects.create(organization=self.agency, name="Clínica")
        self.client.force_login(self.manager.user)
        response = self.client.get(reverse("report"), {"client": other_client.pk, "month": "2026-10"})
        self.assertEqual(response.context["client"], self.bakery)  # falls back to a visible client
