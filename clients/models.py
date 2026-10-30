from django.db import models


class Client(models.Model):
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


class ClientAccess(models.Model):
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


class ClientBriefing(models.Model):
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
