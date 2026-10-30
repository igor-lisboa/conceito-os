from django.urls import path

from . import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification_list"),
    path("<int:pk>/abrir/", views.NotificationOpenView.as_view(), name="notification_open"),
    path("marcar-todas/", views.NotificationReadAllView.as_view(), name="notification_read_all"),
]
