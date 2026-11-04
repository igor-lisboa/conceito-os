from django.urls import path

from . import views

urlpatterns = [
    path("", views.TaskListView.as_view(), name="task_list"),
    path("new/", views.TaskCreateView.as_view(), name="task_create"),
    path("<uuid:pk>/complete/", views.TaskToggleView.as_view(), name="task_toggle"),
]
