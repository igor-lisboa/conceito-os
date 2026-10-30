from django.urls import path

from . import views

urlpatterns = [
    path("", views.ContentListView.as_view(), name="content_list"),
    path("novo/", views.ContentCreateView.as_view(), name="content_create"),
    path("<int:pk>/", views.ContentDetailView.as_view(), name="content_detail"),
    path("<int:pk>/versao/", views.ContentVersionView.as_view(), name="content_version"),
    path("<int:pk>/acao/<str:action>/", views.ContentActionView.as_view(), name="content_action"),
]
