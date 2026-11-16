"""A lead's personal data can be anonymized; the pipeline record stays (DAT-011, D-17)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.core.audit import AuditEvent
from apps.core.testing import make_membership, make_organization, make_owner
from apps.crm.anonymize import ANONYMIZED_NAME, LEAD_ANONYMIZED, anonymize_lead
from apps.crm.models import Lead


class LeadAnonymizeTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.lead = Lead.objects.create(
            organization=self.agency, name="Ana Souza", contact="ana@example.com",
            notes="Quer fazer 3 posts", next_action="Ligar", stage="meeting",
        )

    def test_the_personal_fields_are_replaced_and_the_stage_stays(self):
        anonymize_lead(self.owner, self.lead)

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.name, ANONYMIZED_NAME)
        self.assertEqual(self.lead.contact, "")
        self.assertEqual(self.lead.notes, "")
        self.assertEqual(self.lead.next_action, "")
        self.assertEqual(self.lead.stage, "meeting")

    def test_it_is_audited_without_the_personal_data(self):
        anonymize_lead(self.owner, self.lead)

        event = AuditEvent.objects.get(action=LEAD_ANONYMIZED)
        self.assertNotIn("Ana Souza", str(event.metadata))
        self.assertNotIn("ana@example.com", str(event.metadata))

    def test_anonymizing_twice_does_nothing_new(self):
        anonymize_lead(self.owner, self.lead)
        anonymize_lead(self.owner, self.lead)
        self.assertEqual(AuditEvent.objects.filter(action=LEAD_ANONYMIZED).count(), 1)

    def test_a_manager_without_crm_access_cannot_anonymize(self):
        manager = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")
        self.client.force_login(manager.user)

        self.client.post(reverse("lead_anonymize", args=[self.lead.pk]))

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.name, "Ana Souza")

    def test_the_owner_anonymizes_from_the_board(self):
        self.client.force_login(self.owner.user)
        self.client.post(reverse("lead_anonymize", args=[self.lead.pk]))
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.name, ANONYMIZED_NAME)

    def test_another_organizations_lead_is_not_found(self):
        other = make_owner(make_organization("Outra"))
        self.client.force_login(other.user)
        response = self.client.post(reverse("lead_anonymize", args=[self.lead.pk]))
        self.assertEqual(response.status_code, 404)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.name, "Ana Souza")
