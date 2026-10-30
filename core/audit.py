from .models import AuditEvent


class DjangoAuditLog:
    """Adapter that writes audit events to the database.

    The application layer only knows the `record` method (see the AuditLog
    port in production/application/ports.py).
    """

    def record(self, *, organization_id, actor_user_id, action, entity_type, entity_id, metadata):
        return AuditEvent.objects.create(
            organization_id=organization_id,
            actor_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
        )


def record_event(*, organization, actor, action, entity, metadata=None):
    """Shortcut for simple (non-DDD) services such as clients/services.py."""
    return DjangoAuditLog().record(
        organization_id=organization.pk,
        actor_user_id=actor.pk if actor else None,
        action=action,
        entity_type=type(entity).__name__,
        entity_id=entity.pk,
        metadata=metadata,
    )
