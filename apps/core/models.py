import uuid

from django.conf import settings
from django.db import models


class UUIDModel(models.Model):
    """Base for every table: the primary key is a GUID (UUID), not a counting number.

    Why: numbers in URLs (/content/12/) reveal how many records exist and let people
    guess neighbours. A GUID cannot be guessed, and it is the same on every database.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class AuditEventQuerySet(models.QuerySet):
    """Bulk writes skip model save/delete, so they are refused here too (SEC-007)."""

    def update(self, **kwargs):
        raise RuntimeError("Audit events are append-only and cannot be changed.")

    def delete(self):
        raise RuntimeError("Audit events are append-only and cannot be deleted.")


class AuditEvent(UUIDModel):
    """A record of something that happened. Rows are append-only: they can be
    created and read, but never edited or deleted (see save/delete below)."""

    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="audit_events")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="audit_events"
    )
    action = models.CharField(max_length=60)
    entity_type = models.CharField(max_length=60)
    entity_id = models.UUIDField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AuditEventQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "entity_type", "entity_id"])]

    def __str__(self):
        return f"{self.action} on {self.entity_type}#{self.entity_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise RuntimeError("Audit events are append-only and cannot be changed.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RuntimeError("Audit events are append-only and cannot be deleted.")
