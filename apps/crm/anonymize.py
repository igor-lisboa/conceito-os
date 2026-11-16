"""Anonymize a lead on request (DAT-011, D-17): the record stays, the personal fields go.

A lead is a prospect, so its name, contact details and notes are personal data. They are
replaced by a marker; the stage, source and dates stay, so the pipeline history is kept.
"""

from django.db import transaction

from apps.accounts.permissions import Capability, require_capability
from apps.core.audit import record_event
from apps.core.exceptions import DomainError

LEAD_ANONYMIZED = "lead.anonymized"
ANONYMIZED_NAME = "Anonymized lead"


@transaction.atomic
def anonymize_lead(membership, lead):
    require_capability(membership, Capability.MANAGE_CRM)
    if lead.organization_id != membership.organization_id:
        raise DomainError("This lead belongs to another organization.")
    if lead.name == ANONYMIZED_NAME:
        return lead  # already anonymized

    lead.name = ANONYMIZED_NAME
    lead.contact = ""
    lead.notes = ""
    lead.next_action = ""
    lead.next_action_date = None
    lead.save(update_fields=["name", "contact", "notes", "next_action", "next_action_date", "updated_at"])
    record_event(
        organization=membership.organization,
        actor=membership.user,
        action=LEAD_ANONYMIZED,
        entity=lead,
        metadata={"stage": lead.stage},
    )
    return lead
