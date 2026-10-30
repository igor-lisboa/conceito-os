from django.urls import path

from . import views

urlpatterns = [
    path("leads/", views.LeadBoardView.as_view(), name="lead_board"),
    path("leads/novo/", views.LeadCreateView.as_view(), name="lead_create"),
    path("leads/<uuid:pk>/etapa/", views.LeadStageView.as_view(), name="lead_stage"),
    path("propostas/", views.ProposalListView.as_view(), name="proposal_list"),
    path("propostas/nova/", views.ProposalCreateView.as_view(), name="proposal_create"),
    path("propostas/<uuid:pk>/status/", views.ProposalStatusView.as_view(), name="proposal_status"),
]
