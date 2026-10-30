"""Who can do what.

This file is the single place where the role matrix from
specs/product/01-roles-permissions.md is written down in code.

It works with a Membership (web edge) or an Actor (application core): both have
a `role` attribute, which is all it needs.

Two rules apply on top of these capabilities and are NOT here:
- which clients an actor can see (Actor.client_ids, built in core/actors.py)
- which content a freelancer can edit (production/domain/policy.py)
"""

from apps.core.exceptions import Forbidden

from .roles import Role


class Capability:
    ACCESS_INTERNAL = "access_internal"  # use the internal workspace
    ACCESS_PORTAL = "access_portal"  # use the client portal
    SEE_ALL_CLIENTS = "see_all_clients"  # without this, only assigned clients are visible
    CREATE_CLIENT = "create_client"
    EDIT_BRIEFING = "edit_briefing"
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    APPROVE_INTERNAL = "approve_internal"
    CLIENT_APPROVE = "client_approve"
    SCHEDULE_CONTENT = "schedule_content"
    ARCHIVE_CLIENT = "archive_client"
    MANAGE_TEAM = "manage_team"  # invite and remove members, grant client access
    VIEW_AUDIT = "view_audit"
    MANAGE_CRM = "manage_crm"  # leads and proposals
    ENTER_METRICS = "enter_metrics"  # manual metric entry for reports


ROLE_CAPABILITIES = {
    Role.OWNER: {
        Capability.ACCESS_INTERNAL,
        Capability.SEE_ALL_CLIENTS,
        Capability.CREATE_CLIENT,
        Capability.ARCHIVE_CLIENT,
        Capability.EDIT_BRIEFING,
        Capability.CREATE_CONTENT,
        Capability.EDIT_CONTENT,
        Capability.APPROVE_INTERNAL,
        Capability.SCHEDULE_CONTENT,
        Capability.MANAGE_TEAM,
        Capability.VIEW_AUDIT,
        Capability.MANAGE_CRM,
        Capability.ENTER_METRICS,
    },
    Role.ACCOUNT_MANAGER: {
        Capability.ACCESS_INTERNAL,
        Capability.CREATE_CLIENT,
        Capability.ARCHIVE_CLIENT,
        Capability.EDIT_BRIEFING,
        Capability.CREATE_CONTENT,
        Capability.EDIT_CONTENT,
        Capability.APPROVE_INTERNAL,
        Capability.SCHEDULE_CONTENT,
        Capability.MANAGE_CRM,
        Capability.ENTER_METRICS,
    },
    Role.CREATIVE: {
        Capability.ACCESS_INTERNAL,
        Capability.EDIT_BRIEFING,
        Capability.CREATE_CONTENT,
        Capability.EDIT_CONTENT,
        Capability.ENTER_METRICS,
    },
    # Freelancers only edit content assigned to them (checked by the content policy).
    Role.FREELANCER: {
        Capability.ACCESS_INTERNAL,
        Capability.EDIT_CONTENT,
    },
    Role.CLIENT: {
        Capability.ACCESS_PORTAL,
        Capability.CLIENT_APPROVE,
    },
}


def has_capability(subject, capability):
    """True if the subject's role grants the capability.

    `subject` is a Membership, an Actor, or None (None grants nothing).
    """
    if subject is None:
        return False
    return capability in ROLE_CAPABILITIES.get(Role(subject.role), set())


def require_capability(subject, capability):
    """Raise Forbidden when the subject's role lacks the capability."""
    if not has_capability(subject, capability):
        raise Forbidden(f"Sem permissão: {capability}")
