"""Monthly metrics typed in by the team (manual entry, PD-02). Missing values show as N/D."""

from django.conf import settings
from django.db import models

from core.choices import translated_choices
from core.enums import LabeledEnum
from core.models import UUIDModel


class Platform(LabeledEnum):
    INSTAGRAM = ("instagram", "Instagram")
    TIKTOK = ("tiktok", "TikTok")


class Metric(LabeledEnum):
    REACH = ("reach", "Reach")
    INTERACTIONS = ("interactions", "Interactions")
    SAVES = ("saves", "Saves")
    FOLLOWERS = ("followers", "Followers")
    VIEWS = ("views", "Views")


# The metrics a monthly report looks for on each network (spec MET-006).
EXPECTED_METRICS = {
    Platform.INSTAGRAM.value: [Metric.REACH, Metric.INTERACTIONS, Metric.SAVES, Metric.FOLLOWERS],
    Platform.TIKTOK.value: [Metric.VIEWS, Metric.INTERACTIONS, Metric.FOLLOWERS],
}


class MetricEntry(UUIDModel):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="metric_entries")
    platform = models.CharField(max_length=20, choices=translated_choices(Platform))
    metric = models.CharField(max_length=20, choices=translated_choices(Metric))
    month = models.DateField(help_text="First day of the month the value refers to.")
    value = models.PositiveBigIntegerField()
    # Always "manual" for now: no network API is connected yet (see docs/technical-debt.md, TD-19).
    source = models.CharField(max_length=20, default="manual", editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-month", "platform", "metric"]
        constraints = [
            models.UniqueConstraint(
                fields=["client", "platform", "metric", "month"], name="unique_metric_per_client_month"
            ),
        ]

    def __str__(self):
        return f"{self.client} {self.platform} {self.metric} {self.month:%Y-%m}"
