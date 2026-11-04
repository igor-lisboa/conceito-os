from django.urls import path

from . import planning, views

urlpatterns = [
    path("", views.ContentListView.as_view(), name="content_list"),
    path("new/", views.ContentCreateView.as_view(), name="content_create"),
    path("calendar/", planning.ContentCalendarView.as_view(), name="content_calendar"),
    path("board/", planning.ContentBoardView.as_view(), name="content_board"),
    path("<uuid:pk>/", views.ContentDetailView.as_view(), name="content_detail"),
    path("<uuid:pk>/version/", views.ContentVersionView.as_view(), name="content_version"),
    path("<uuid:pk>/action/<str:action>/", views.ContentActionView.as_view(), name="content_action"),
    path("<uuid:pk>/planned-date/", views.ContentRescheduleView.as_view(), name="content_reschedule"),
    path("<uuid:pk>/comment/", views.ContentCommentView.as_view(), name="content_comment"),
    path("<uuid:pk>/comment/<uuid:comment_pk>/edit/", views.ContentCommentEditView.as_view(),
         name="content_comment_edit"),
    path("<uuid:pk>/comment/<uuid:comment_pk>/delete/", views.ContentCommentDeleteView.as_view(),
         name="content_comment_delete"),
    path("<uuid:pk>/duplicate/", planning.ContentDuplicateView.as_view(), name="content_duplicate"),
]
