from django.urls import path

from . import views

urlpatterns = [
    path("leads/", views.LeadBoardView.as_view(), name="lead_board"),
    path("leads/new/", views.LeadCreateView.as_view(), name="lead_create"),
    path("leads/<uuid:pk>/stage/", views.LeadStageView.as_view(), name="lead_stage"),
    path("proposals/", views.ProposalListView.as_view(), name="proposal_list"),
    path("proposals/new/", views.ProposalCreateView.as_view(), name="proposal_create"),
    path("proposals/<uuid:pk>/status/", views.ProposalStatusView.as_view(), name="proposal_status"),
]
