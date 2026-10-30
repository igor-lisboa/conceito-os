"""Leads and proposals, typed in by the team (TD-01, PD-02)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import Role
from apps.clients.models import Client
from apps.core.testing import make_membership, make_organization, make_owner
from apps.crm.models import Lead, LeadStage, Proposal, ProposalStatus


class LeadTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        self.lead = Lead.objects.create(organization=self.agency, name="Confeitaria Doce Lar")

    def test_owner_creates_a_lead_in_the_organization(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("lead_create"),
            {"name": "Clínica Sorriso", "source": "referral", "stage": "new", "notes": "Indicação da Padaria"},
        )
        lead = Lead.objects.get(name="Clínica Sorriso")
        self.assertEqual(lead.organization, self.agency)
        self.assertEqual(lead.source, "referral")

    def test_board_groups_leads_by_stage(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("lead_board"))
        self.assertEqual(len(response.context["columns"]), len(LeadStage))
        new_column = next(leads for stage, leads in response.context["columns"] if stage == LeadStage.NEW)
        self.assertEqual(new_column, [self.lead])

    def test_moving_a_lead_to_another_stage(self):
        self.client.force_login(self.manager.user)
        self.client.post(reverse("lead_stage", args=[self.lead.pk]), {"stage": "meeting"})
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.stage, LeadStage.MEETING.value)

    def test_an_unknown_stage_is_refused(self):
        self.client.force_login(self.owner.user)
        self.client.post(reverse("lead_stage", args=[self.lead.pk]), {"stage": "dragons"})
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.stage, LeadStage.NEW.value)

    def test_creatives_cannot_see_the_sales_pipeline(self):
        creative = make_membership(self.agency, Role.CREATIVE)
        self.client.force_login(creative.user)
        self.assertEqual(self.client.get(reverse("lead_board")).status_code, 403)

    def test_leads_of_another_organization_cannot_be_moved(self):
        other = make_owner(make_organization("Outra"))
        self.client.force_login(other.user)
        self.client.post(reverse("lead_stage", args=[self.lead.pk]), {"stage": "won"})
        self.assertEqual(self.client.get(reverse("lead_board")).status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.stage, LeadStage.NEW.value)


class ProposalTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")

    def test_owner_writes_a_proposal_linked_to_a_client(self):
        self.client.force_login(self.owner.user)
        self.client.post(
            reverse("proposal_create"),
            {"title": "Gestão de maio", "amount": "2500.00", "status": "draft", "client": self.bakery.pk},
        )
        proposal = Proposal.objects.get(title="Gestão de maio")
        self.assertEqual(str(proposal.amount), "2500.00")
        self.assertEqual(proposal.client, self.bakery)

    def test_an_amount_that_is_not_a_number_is_refused(self):
        self.client.force_login(self.owner.user)
        self.client.post(reverse("proposal_create"), {"title": "X", "amount": "muito", "status": "draft"})
        self.assertFalse(Proposal.objects.exists())

    def test_status_can_be_updated(self):
        proposal = Proposal.objects.create(organization=self.agency, title="Y", amount=100, status="draft")
        self.client.force_login(self.owner.user)
        self.client.post(reverse("proposal_status", args=[proposal.pk]), {"status": "accepted"})
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, ProposalStatus.ACCEPTED.value)

    def test_client_users_cannot_open_proposals(self):
        portal_user = make_membership(self.agency, Role.CLIENT)
        self.client.force_login(portal_user.user)
        self.assertEqual(self.client.get(reverse("proposal_list")).status_code, 403)
        self.assertTrue(Client.objects.filter(pk=self.bakery.pk).exists())
