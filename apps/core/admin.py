from django.contrib import admin

from .models import AuditEvent


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """Admin that can only look. Use it for records that must change through the
    application (so the rules are always applied), never by hand in the admin."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditEvent)
class AuditEventAdmin(ReadOnlyModelAdmin):
    list_display = ("created_at", "action", "entity_type", "entity_id", "actor", "organization")
    list_filter = ("action", "entity_type", "organization")
    search_fields = ("action",)
