"""CRM access is granted per person by an owner (D-16, answer 4B)."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts import team
from apps.accounts.models import Membership
from apps.accounts.roles import Role
from apps.core.exceptions import DomainError, Forbidden
from apps.core.testing import make_membership, make_organization, make_owner


class CrmAccessTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER, username="ana")

    def test_an_account_manager_without_the_flag_cannot_open_the_lead_board(self):
        self.client.force_login(self.manager.user)
        self.assertEqual(self.client.get(reverse("lead_board")).status_code, 403)

    def test_the_owner_can_grant_and_stop_crm_access(self):
        team.set_crm_access(self.owner, self.manager, allowed=True)
        self.client.force_login(self.manager.user)
        self.assertEqual(self.client.get(reverse("lead_board")).status_code, 200)

        team.set_crm_access(self.owner, self.manager, allowed=False)
        self.assertEqual(self.client.get(reverse("lead_board")).status_code, 403)

    def test_an_account_manager_cannot_grant_it_to_themselves(self):
        with self.assertRaises(Forbidden):
            team.set_crm_access(self.manager, self.manager, allowed=True)
        self.manager.refresh_from_db()
        self.assertFalse(self.manager.crm_access)

    def test_owners_always_have_crm_without_the_flag(self):
        self.client.force_login(self.owner.user)
        self.assertEqual(self.client.get(reverse("lead_board")).status_code, 200)

    def test_inviting_with_the_flag_sets_it(self):
        invited = team.invite_member(
            self.owner, email="bia@example.com", role=Role.ACCOUNT_MANAGER, crm_access=True
        )
        self.assertTrue(invited.crm_access)

    def test_changes_are_audited(self):
        from apps.core.audit import AuditEvent

        team.set_crm_access(self.owner, self.manager, allowed=True)
        self.assertTrue(AuditEvent.objects.filter(action=team.MEMBER_CRM_ACCESS_CHANGED).exists())

    def test_a_removed_person_cannot_be_given_access(self):
        team.remove_member(self.owner, self.manager)
        with self.assertRaises(DomainError):
            team.set_crm_access(self.owner, Membership.all_objects.get(pk=self.manager.pk), allowed=True)

    def test_the_owner_toggles_it_from_the_team_page(self):
        self.client.force_login(self.owner.user)
        self.client.post(reverse("team_crm_access", args=[self.manager.pk]), {"allowed": "1"})
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.crm_access)
