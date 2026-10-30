"""Tasks: small follow-ups for a client or a piece, with an owner and a due date (TD-06)."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    client = models.ForeignKey(
        "clients.Client", null=True, blank=True, on_delete=models.CASCADE, related_name="tasks"
    )
    content = models.ForeignKey(
        "production.ContentItem", null=True, blank=True, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=160)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks"
    )
    due_date = models.DateField(null=True, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["done_at", "due_date", "id"]

    def __str__(self):
        return self.title

    @property
    def is_done(self):
        return self.done_at is not None

    def mark_done(self, done=True):
        self.done_at = timezone.now() if done else None
        self.save(update_fields=["done_at"])
