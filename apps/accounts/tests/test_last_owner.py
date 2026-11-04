"""The last owner of an organization cannot be removed (AUTH-012, PRM-007)."""

from django.test import TestCase

from apps.accounts import team
from apps.accounts.models import Membership
from apps.accounts.roles import Role
from apps.core.exceptions import DomainError
from apps.core.testing import make_membership, make_organization, make_owner


class LastOwnerTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.only_owner = make_owner(self.agency)

    def test_the_only_owner_cannot_be_removed_by_another_team_manager(self):
        # The actor has owner rights but is not a saved member, so the database holds one owner only.
        # The removal rule must refuse, not the role check.
        outsider_user = make_membership(self.agency, Role.CREATIVE, username="chefe").user
        acting = Membership(user=outsider_user, organization=self.agency, role=Role.OWNER)

        with self.assertRaises(DomainError):
            team.remove_member(acting, self.only_owner)

        self.assertTrue(Membership.objects.filter(pk=self.only_owner.pk).exists())

    def test_removing_one_of_two_owners_is_allowed(self):
        second = make_owner(self.agency)

        team.remove_member(self.only_owner, second)

        self.assertFalse(Membership.objects.filter(pk=second.pk).exists())
        self.assertTrue(Membership.objects.filter(pk=self.only_owner.pk).exists())
