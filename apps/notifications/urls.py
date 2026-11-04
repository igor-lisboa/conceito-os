from django.urls import path

from . import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification_list"),
    path("<uuid:pk>/open/", views.NotificationOpenView.as_view(), name="notification_open"),
    path("mark-all-read/", views.NotificationReadAllView.as_view(), name="notification_read_all"),
]
