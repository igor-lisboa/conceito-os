from django.urls import path

from . import views

urlpatterns = [
    path("", views.ReportView.as_view(), name="report"),
    path("novo/", views.MetricEntryView.as_view(), name="metric_entry"),
]
