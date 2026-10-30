"""Edge helper: turns the Django Membership (plus ClientAccess rows) into an Actor.

This is the one place where the web layer translates "who is logged in" into the
plain Actor object used by the application core.
"""

from apps.accounts.models import Role
from apps.accounts.permissions import Capability, has_capability
from apps.clients.models import ClientAccess

from .actor import Actor


def actor_for(membership):
    if membership is None:
        return None
    client_ids = frozenset(
        ClientAccess.objects.filter(membership=membership).values_list("client_id", flat=True)
    )
    return Actor(
        user_id=membership.user_id,
        organization_id=membership.organization_id,
        role=membership.role,
        sees_all_clients=has_capability(membership, Capability.SEE_ALL_CLIENTS),
        sees_only_assigned=membership.role == Role.FREELANCER,
        client_ids=client_ids,
    )
