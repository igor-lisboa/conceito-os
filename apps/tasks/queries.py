from apps.accounts.permissions import Capability, has_capability
from apps.accounts.roles import Role
from apps.clients.queries import visible_clients

from .models import Task


def visible_tasks(membership):
    """Tasks this person may see.

    - a task linked to a client follows that client's visibility;
    - a task with no client is visible to owners and account managers only.
    """
    queryset = Task.objects.filter(organization=membership.organization)
    if has_capability(membership, Capability.SEE_ALL_CLIENTS):
        return queryset

    allowed_clients = visible_clients(membership)
    with_client = queryset.filter(client__in=allowed_clients)
    if membership.role == Role.ACCOUNT_MANAGER.value:
        return with_client | queryset.filter(client__isnull=True)
    return with_client
