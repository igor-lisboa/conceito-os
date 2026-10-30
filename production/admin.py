from django.contrib import admin

from core.admin import ReadOnlyModelAdmin

from .models import Approval, ContentItem, ContentVersion


@admin.register(ContentItem)
class ContentItemAdmin(ReadOnlyModelAdmin):
    list_display = ("title", "client", "state", "scheduled_for", "published_at")
    list_filter = ("state", "channel", "client__organization")
    search_fields = ("title",)


@admin.register(ContentVersion)
class ContentVersionAdmin(ReadOnlyModelAdmin):
    list_display = ("content", "number", "created_at")


@admin.register(Approval)
class ApprovalAdmin(ReadOnlyModelAdmin):
    list_display = ("content", "stage", "decision", "created_at")
    list_filter = ("stage", "decision")
