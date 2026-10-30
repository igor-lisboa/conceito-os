from django.urls import path

from . import views

urlpatterns = [
    path("", views.ClientListView.as_view(), name="client_list"),
    path("novo/", views.ClientCreateView.as_view(), name="client_create"),
    path("<uuid:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("<uuid:pk>/briefing/", views.BriefingUpdateView.as_view(), name="client_briefing"),
    path("<uuid:pk>/biblioteca/novo/", views.AssetCreateView.as_view(), name="client_asset_create"),
]
