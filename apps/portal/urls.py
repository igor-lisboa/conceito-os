from django.urls import path

from . import sections, views

urlpatterns = [
    path("", views.PortalListView.as_view(), name="portal_list"),
    path("<uuid:pk>/", views.PortalDetailView.as_view(), name="portal_detail"),
    path("<uuid:pk>/comment/", views.PortalCommentView.as_view(), name="portal_comment"),
    path("calendar/", sections.PortalCalendarView.as_view(), name="portal_calendar"),
    path("results/", sections.PortalResultsView.as_view(), name="portal_results"),
    path("files/", sections.PortalFilesView.as_view(), name="portal_files"),
    path("contact/", sections.PortalContactView.as_view(), name="portal_contact"),
]
