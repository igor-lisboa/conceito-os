from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # language switch endpoint
    path("accounts/", include("apps.accounts.urls")),
    path("clientes/", include("apps.clients.urls")),
    path("conteudos/", include("apps.production.urls")),
    path("portal/", include("apps.portal.urls")),
    path("notificacoes/", include("apps.notifications.urls")),
    path("comercial/", include("apps.crm.urls")),
    path("relatorios/", include("apps.reports.urls")),
    path("tarefas/", include("apps.tasks.urls")),
    path("", include("apps.core.urls")),
]
