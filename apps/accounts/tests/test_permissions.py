from django.test import SimpleTestCase

from apps.accounts.permissions import Capability, has_capability, require_capability
from apps.accounts.roles import Role
from apps.core.exceptions import Forbidden


class FakeMembership:
    """Stands in for Membership: the permission check only reads `role`."""

    def __init__(self, role):
        self.role = role.value


class RoleMatrixTests(SimpleTestCase):
    """These tests pin the role matrix from specs/product/01-roles-permissions.md.
    If someone changes a permission, the matching test must change on purpose."""

    def test_owner_can_do_everything_internal(self):
        owner = FakeMembership(Role.OWNER)
        for capability in (
            Capability.ACCESS_INTERNAL,
            Capability.SEE_ALL_CLIENTS,
            Capability.CREATE_CLIENT,
            Capability.APPROVE_INTERNAL,
            Capability.SCHEDULE_CONTENT,
        ):
            self.assertTrue(has_capability(owner, capability), capability)

    def test_freelancer_can_edit_but_never_approve_or_schedule(self):
        freelancer = FakeMembership(Role.FREELANCER)
        self.assertTrue(has_capability(freelancer, Capability.EDIT_CONTENT))
        self.assertFalse(has_capability(freelancer, Capability.CREATE_CONTENT))
        self.assertFalse(has_capability(freelancer, Capability.APPROVE_INTERNAL))
        self.assertFalse(has_capability(freelancer, Capability.SCHEDULE_CONTENT))
        self.assertFalse(has_capability(freelancer, Capability.SEE_ALL_CLIENTS))

    def test_creative_cannot_approve_or_schedule(self):
        creative = FakeMembership(Role.CREATIVE)
        self.assertTrue(has_capability(creative, Capability.EDIT_CONTENT))
        self.assertFalse(has_capability(creative, Capability.APPROVE_INTERNAL))
        self.assertFalse(has_capability(creative, Capability.SCHEDULE_CONTENT))

    def test_client_has_only_portal_access(self):
        client_user = FakeMembership(Role.CLIENT)
        self.assertTrue(has_capability(client_user, Capability.ACCESS_PORTAL))
        self.assertTrue(has_capability(client_user, Capability.CLIENT_APPROVE))
        self.assertFalse(has_capability(client_user, Capability.ACCESS_INTERNAL))
        self.assertFalse(has_capability(client_user, Capability.EDIT_CONTENT))

    def test_no_membership_grants_nothing(self):
        self.assertFalse(has_capability(None, Capability.ACCESS_INTERNAL))

    def test_require_capability_raises_forbidden(self):
        with self.assertRaises(Forbidden):
            require_capability(FakeMembership(Role.CLIENT), Capability.APPROVE_INTERNAL)
