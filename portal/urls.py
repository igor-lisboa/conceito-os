from django.urls import path

from . import views

urlpatterns = [
    path("", views.PortalListView.as_view(), name="portal_list"),
    path("<int:pk>/", views.PortalDetailView.as_view(), name="portal_detail"),
]
