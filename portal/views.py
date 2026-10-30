"""Client portal: a client sees and decides on their own content, nothing internal.

The portal reuses the same service as the internal app, so a client can only do
what the content lifecycle allows (approve or request changes while the piece
is in client review).
"""

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext
from django.views.generic import DetailView, ListView

from accounts.mixins import CapabilityRequiredMixin
from accounts.permissions import Capability
from core.actors import actor_for
from core.http import run_action
from production.composition import build_content_service
from production.domain.content import ApprovalStage
from production.domain.states import ContentState
from production.models import Approval
from production.queries import visible_content

from .forms import ClientDecisionForm


class PortalListView(CapabilityRequiredMixin, ListView):
    required_capability = Capability.ACCESS_PORTAL
    template_name = "portal/list.html"
    context_object_name = "items"

    def get_queryset(self):
        return (
            visible_content(actor_for(self.request.membership))
            .filter(state=ContentState.CLIENT_REVIEW)
            .select_related("client")
        )


class PortalDetailView(CapabilityRequiredMixin, DetailView):
    required_capability = Capability.ACCESS_PORTAL
    template_name = "portal/detail.html"

    def get_queryset(self):
        return visible_content(actor_for(self.request.membership)).select_related("client")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest"] = self.object.versions.order_by("-number").first()
        # Only the client-stage history. Internal comments never reach the portal.
        context["client_approvals"] = Approval.objects.filter(
            content=self.object, stage=ApprovalStage.CLIENT.value
        ).select_related("version")
        context["decision_form"] = ClientDecisionForm()
        return context

    def post(self, request, *args, **kwargs):
        content = self.get_object()
        form = ClientDecisionForm(request.POST)
        if not form.is_valid():
            messages.error(request, gettext("Choose approve or request changes."))
            return redirect("portal_detail", pk=content.pk)

        approve = form.cleaned_data["decision"] == ClientDecisionForm.APPROVE
        run_action(
            request,
            lambda: build_content_service().decide_client(
                actor_for(request.membership),
                content.pk,
                approve=approve,
                comment=form.cleaned_data["comment"],
            ),
            success_message="Thank you! Your decision was recorded.",
        )
        return redirect("portal_detail", pk=content.pk)
