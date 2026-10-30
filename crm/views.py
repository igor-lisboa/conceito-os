from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views import View
from django.views.generic import CreateView, ListView

from accounts.mixins import CapabilityRequiredMixin
from accounts.permissions import Capability

from .forms import LeadForm, ProposalForm
from .models import Lead, LeadStage, Proposal, ProposalStatus


class LeadBoardView(CapabilityRequiredMixin, ListView):
    """Leads grouped by stage, so the team sees the pipeline at a glance."""

    required_capability = Capability.MANAGE_CRM
    template_name = "crm/lead_board.html"
    context_object_name = "leads"

    def get_queryset(self):
        return Lead.objects.filter(organization=self.request.membership.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        leads = list(context["leads"])
        context["columns"] = [
            (stage, [lead for lead in leads if lead.stage == stage.value]) for stage in LeadStage
        ]
        context["stage_choices"] = [(value, gettext(label)) for value, label in LeadStage.choices()]
        return context


class LeadCreateView(CapabilityRequiredMixin, CreateView):
    required_capability = Capability.MANAGE_CRM
    template_name = "crm/lead_form.html"
    form_class = LeadForm
    success_url = reverse_lazy("lead_board")

    def form_valid(self, form):
        form.instance.organization = self.request.membership.organization
        messages.success(self.request, gettext("Lead saved."))
        return super().form_valid(form)


class LeadStageView(CapabilityRequiredMixin, View):
    required_capability = Capability.MANAGE_CRM
    http_method_names = ["post"]

    def post(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk, organization=request.membership.organization)
        stage = request.POST.get("stage", "")
        if stage not in LeadStage.values():
            messages.error(request, gettext("Unknown stage."))
        else:
            lead.stage = stage
            lead.save(update_fields=["stage", "updated_at"])
            messages.success(request, gettext("Stage updated."))
        return redirect("lead_board")


class ProposalListView(CapabilityRequiredMixin, ListView):
    required_capability = Capability.MANAGE_CRM
    template_name = "crm/proposal_list.html"
    context_object_name = "proposals"

    def get_queryset(self):
        return Proposal.objects.filter(organization=self.request.membership.organization).select_related(
            "lead", "client"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = [(value, gettext(label)) for value, label in ProposalStatus.choices()]
        return context


class ProposalCreateView(CapabilityRequiredMixin, CreateView):
    required_capability = Capability.MANAGE_CRM
    template_name = "crm/proposal_form.html"
    form_class = ProposalForm
    success_url = reverse_lazy("proposal_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["membership"] = self.request.membership
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.request.membership.organization
        messages.success(self.request, gettext("Proposal saved."))
        return super().form_valid(form)


class ProposalStatusView(CapabilityRequiredMixin, View):
    required_capability = Capability.MANAGE_CRM
    http_method_names = ["post"]

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk, organization=request.membership.organization)
        status = request.POST.get("status", "")
        if status not in ProposalStatus.values():
            messages.error(request, gettext("Unknown status."))
        else:
            proposal.status = status
            proposal.save(update_fields=["status", "updated_at"])
            messages.success(request, gettext("Status updated."))
        return redirect("proposal_list")
