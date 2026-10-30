from django.db import transaction
from django.utils import timezone

from accounts.permissions import Capability, require_capability
from core.audit import record_event
from core.exceptions import NotFound

from .models import Client, ClientAccess, ClientBriefing
from .queries import visible_clients

CLIENT_CREATED = "client.created"
BRIEFING_UPDATED = "briefing.updated"


@transaction.atomic
def create_client(membership, *, name, client_approval_required=True):
    """Create a client and give the creator access to it, so they can see what they made."""
    require_capability(membership, Capability.CREATE_CLIENT)

    client = Client.objects.create(
        organization=membership.organization,
        name=name,
        client_approval_required=client_approval_required,
    )
    ClientAccess.objects.create(organization=membership.organization, client=client, membership=membership)
    ClientBriefing.objects.create(organization=membership.organization, client=client)

    record_event(
        organization=membership.organization,
        actor=membership.user,
        action=CLIENT_CREATED,
        entity=client,
        metadata={"name": name},
    )
    return client


CLIENT_ARCHIVED = "client.archived"


@transaction.atomic
def archive_client(membership, client):
    """Hide a client from the lists and stop new content for it. Its history is kept."""
    require_capability(membership, Capability.ARCHIVE_CLIENT)
    if not visible_clients(membership).filter(pk=client.pk).exists():
        raise NotFound("Client not found.")
    if client.archived_at is not None:
        return client

    client.archived_at = timezone.now()
    client.save(update_fields=["archived_at"])
    record_event(
        organization=membership.organization,
        actor=membership.user,
        action=CLIENT_ARCHIVED,
        entity=client,
        metadata={},
    )
    return client


@transaction.atomic
def update_briefing(membership, client, **fields):
    """Save briefing answers. `fields` must be names of ClientBriefing text fields."""
    require_capability(membership, Capability.EDIT_BRIEFING)
    if not visible_clients(membership).filter(pk=client.pk).exists():
        raise NotFound("Client not found.")

    briefing = client.briefing
    for name, value in fields.items():
        setattr(briefing, name, value)
    briefing.save()

    record_event(
        organization=membership.organization,
        actor=membership.user,
        action=BRIEFING_UPDATED,
        entity=briefing,
        metadata={"fields": sorted(fields)},
    )
    return briefing
