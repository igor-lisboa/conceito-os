from django.contrib import admin

from .models import Client, ClientAccess, ClientBriefing


class ClientAccessInline(admin.TabularInline):
    model = ClientAccess
    extra = 0
    fields = ("membership", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "client_approval_required", "created_at")
    list_filter = ("organization",)
    search_fields = ("name",)
    inlines = [ClientAccessInline]


@admin.register(ClientBriefing)
class ClientBriefingAdmin(admin.ModelAdmin):
    list_display = ("client", "updated_at")
