from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # language switch endpoint
    path("accounts/", include("apps.accounts.urls")),
    path("clients/", include("apps.clients.urls")),
    path("content/", include("apps.production.urls")),
    path("portal/", include("apps.portal.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("crm/", include("apps.crm.urls")),
    path("reports/", include("apps.reports.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("", include("apps.core.urls")),
]
