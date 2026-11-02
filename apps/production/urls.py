from django.urls import path

from . import planning, views

urlpatterns = [
    path("", views.ContentListView.as_view(), name="content_list"),
    path("novo/", views.ContentCreateView.as_view(), name="content_create"),
    path("calendario/", planning.ContentCalendarView.as_view(), name="content_calendar"),
    path("quadro/", planning.ContentBoardView.as_view(), name="content_board"),
    path("<uuid:pk>/", views.ContentDetailView.as_view(), name="content_detail"),
    path("<uuid:pk>/versao/", views.ContentVersionView.as_view(), name="content_version"),
    path("<uuid:pk>/acao/<str:action>/", views.ContentActionView.as_view(), name="content_action"),
    path("<uuid:pk>/data-planejada/", views.ContentRescheduleView.as_view(), name="content_reschedule"),
    path("<uuid:pk>/comentario/", views.ContentCommentView.as_view(), name="content_comment"),
    path("<uuid:pk>/duplicar/", planning.ContentDuplicateView.as_view(), name="content_duplicate"),
]
