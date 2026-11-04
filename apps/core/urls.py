from django.urls import path

from .views import AuditLogView, HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("audit/", AuditLogView.as_view(), name="audit_log"),
]
