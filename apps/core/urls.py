from django.urls import path

from .views import AuditLogView, ContactView, HomeView, LandingView

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("dashboard/", HomeView.as_view(), name="home"),
    path("audit/", AuditLogView.as_view(), name="audit_log"),
]
