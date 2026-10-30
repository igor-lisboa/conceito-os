from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # language switch endpoint
    path("accounts/", include("accounts.urls")),
    path("clientes/", include("clients.urls")),
    path("conteudos/", include("production.urls")),
    path("portal/", include("portal.urls")),
    path("", include("core.urls")),
]
