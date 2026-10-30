from django.urls import path

from . import views

urlpatterns = [
    path("", views.ClientListView.as_view(), name="client_list"),
    path("novo/", views.ClientCreateView.as_view(), name="client_create"),
    path("<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("<int:pk>/briefing/", views.BriefingUpdateView.as_view(), name="client_briefing"),
]
