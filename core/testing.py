"""Small helpers that build realistic test data.

Keep test setup readable: a test should say what matters (a role, an
organization) and let these helpers fill in the rest.
"""

from django.contrib.auth import get_user_model

from accounts.models import Membership, Organization, Role

User = get_user_model()


def make_organization(name="Agência Teste"):
    return Organization.objects.create(name=name)


def make_membership(organization, role, username=None):
    """Create a user and make them a member of `organization` with `role`."""
    username = username or f"user-{role}-{User.objects.count() + 1}"
    user = User.objects.create_user(username=username, password="senha-de-teste-123")
    return Membership.objects.create(user=user, organization=organization, role=role)


def make_owner(organization):
    return make_membership(organization, Role.OWNER)
