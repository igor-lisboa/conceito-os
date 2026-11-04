from django.urls import path

from . import views

urlpatterns = [
    path("", views.ReportView.as_view(), name="report"),
    path("new/", views.MetricEntryView.as_view(), name="metric_entry"),
]
