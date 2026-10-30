from django.conf import settings
from django.db import models
from django.utils.translation import gettext

# What each notification says. The text is an English msgid with named placeholders;
# it is translated when shown, so the same notification reads in the viewer's language.
KIND_MESSAGES = {
    "client_review": "“{title}” for {client} is waiting for your approval.",
    "internal_review": "“{title}” for {client} is ready for internal review.",
    "changes_requested": "{client} asked for changes on “{title}”.",
    "approved_by_client": "{client} approved “{title}”.",
    "internal_rejected": "“{title}” needs changes before it goes to the client.",
    "publish_failed": "Publishing “{title}” failed: {reason}",
}


class Notification(models.Model):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    kind = models.CharField(max_length=40, choices=[(kind, kind) for kind in KIND_MESSAGES])
    params = models.JSONField(default=dict, blank=True)
    url = models.CharField(max_length=300)
    # Same event + same person = one notification, even if the event is processed twice.
    event_key = models.CharField(max_length=200)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["recipient", "event_key"], name="unique_notification_per_event"),
        ]

    def __str__(self):
        return self.message

    @property
    def message(self):
        return gettext(KIND_MESSAGES[self.kind]).format(**self.params)

    @property
    def is_unread(self):
        return self.read_at is None
