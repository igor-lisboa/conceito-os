from django.urls import path

from . import views

urlpatterns = [
    path("", views.TaskListView.as_view(), name="task_list"),
    path("nova/", views.TaskCreateView.as_view(), name="task_create"),
    path("<uuid:pk>/concluir/", views.TaskToggleView.as_view(), name="task_toggle"),
]
