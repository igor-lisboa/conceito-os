from accounts.permissions import Capability, has_capability

from .models import Client


def visible_clients(membership, *, include_archived=False):
    """Clients this membership is allowed to see.

    Every query about clients must start from here, so the rule is written once:
    - always limited to the membership's organization (tenant isolation)
    - archived clients are hidden unless asked for
    - owners see all clients of their organization
    - everyone else sees only the clients they were granted
    """
    queryset = Client.objects.filter(organization=membership.organization)
    if not include_archived:
        queryset = queryset.filter(archived_at__isnull=True)
    if has_capability(membership, Capability.SEE_ALL_CLIENTS):
        return queryset
    return queryset.filter(accesses__membership=membership)
