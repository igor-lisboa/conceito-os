from django.urls import path

from . import sections, views

urlpatterns = [
    path("", views.PortalListView.as_view(), name="portal_list"),
    path("<uuid:pk>/", views.PortalDetailView.as_view(), name="portal_detail"),
    path("<uuid:pk>/comentario/", views.PortalCommentView.as_view(), name="portal_comment"),
    path("calendario/", sections.PortalCalendarView.as_view(), name="portal_calendar"),
    path("resultados/", sections.PortalResultsView.as_view(), name="portal_results"),
    path("arquivos/", sections.PortalFilesView.as_view(), name="portal_files"),
    path("contato/", sections.PortalContactView.as_view(), name="portal_contact"),
]
