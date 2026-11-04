"""Persistence models (database tables). They are NOT the domain model.

The domain works with `apps.production.domain.content.Content`. The adapter in
production/adapters/django_repository.py translates between the two. Keeping
them apart lets the domain change without a migration, and the tables change
without touching the rules.
"""

from django.conf import settings
from django.db import models

from apps.core.choices import translated_choices
from apps.core.models import UUIDModel

from .domain.content import ApprovalDecision, ApprovalStage, Channel, ContentFormat
from .domain.states import ContentState


class ContentItem(UUIDModel):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="content_items")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_content",
    )
    title = models.CharField(max_length=160)
    channel = models.CharField(max_length=20, choices=translated_choices(Channel), default=Channel.INSTAGRAM.value)
    content_format = models.CharField(max_length=20, choices=translated_choices(ContentFormat))
    state = models.CharField(max_length=30, choices=translated_choices(ContentState), default=ContentState.DRAFT.value)
    # Copied from the client when the piece is created, so later changes to the
    # client do not silently change the rules of content already in progress.
    client_approval_required = models.BooleanField(default=True)
    # The date the team plans to publish. Editable until the client sees the piece (PRO-016).
    planned_for = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    published_url = models.URLField(max_length=500, blank=True)
    # How the piece was published. Only "manual" until the network integrations exist (INT-010).
    publish_method = models.CharField(max_length=20, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.title


class ContentVersion(UUIDModel):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    content = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name="versions")
    number = models.PositiveIntegerField()
    caption = models.TextField(blank=True)
    cta = models.CharField(max_length=200, blank=True)
    script = models.TextField(blank=True)
    media_url = models.URLField(max_length=500, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(fields=["content", "number"], name="unique_version_number_per_content"),
        ]

    def __str__(self):
        return f"{self.content} v{self.number}"


class Approval(UUIDModel):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    content = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name="approvals")
    version = models.ForeignKey(ContentVersion, on_delete=models.CASCADE, related_name="approvals")
    stage = models.CharField(max_length=20, choices=translated_choices(ApprovalStage))
    decision = models.CharField(max_length=30, choices=translated_choices(ApprovalDecision))
    comment = models.TextField(blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{ApprovalStage(self.stage).label}: {ApprovalDecision(self.decision).label} (v{self.version.number})"


class Comment(UUIDModel):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    content = models.ForeignKey("production.ContentItem", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    # Set when the author edits the comment, so readers can see it changed (TD-S13, PROPOSAL).
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Comment on {self.content_id}"
