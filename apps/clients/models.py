from django.db import models

from apps.core.choices import translated_choices
from apps.core.enums import LabeledEnum
from apps.core.models import UUIDModel


class Client(UUIDModel):
    """A brand served by the agency (not the platform subscriber)."""

    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="clients")
    name = models.CharField(max_length=120)
    # When True, content must be approved by the client before it can be scheduled.
    client_approval_required = models.BooleanField(default=True)
    # Archived clients disappear from lists and accept no new content. Nothing is deleted.
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_client_name_per_org"),
        ]

    def __str__(self):
        return self.name


class ClientAccess(UUIDModel):
    """Lets one membership see one client. Owners see every client without these rows."""

    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="accesses")
    membership = models.ForeignKey(
        "accounts.Membership", on_delete=models.CASCADE, related_name="client_accesses"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["client", "membership"], name="unique_client_access"),
        ]

    def __str__(self):
        return f"{self.membership} -> {self.client}"


class ClientBriefing(UUIDModel):
    """The brand briefing: answers the strategy team needs before creating content."""

    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name="briefing")
    objective = models.TextField(blank=True)
    audience = models.TextField(blank=True)
    tone_of_voice = models.TextField(blank=True)
    competitors = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Briefing of {self.client}"


class AssetKind(LabeledEnum):
    LOGO = ("logo", "Logo")
    FONT = ("font", "Font")
    TEMPLATE = ("template", "Template")
    REFERENCE = ("reference", "Reference")
    OTHER = ("other", "Other")


class BrandAsset(UUIDModel):
    """A link to a brand file kept elsewhere (Drive, Dropbox...). Files are not uploaded yet (PD-03)."""

    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="assets")
    title = models.CharField(max_length=120)
    kind = models.CharField(max_length=20, choices=translated_choices(AssetKind), default=AssetKind.OTHER.value)
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["kind", "title"]

    def __str__(self):
        return self.title
