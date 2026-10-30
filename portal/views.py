"""Client portal: a client sees and decides on their own content, nothing internal.

The portal reuses the same service as the internal app, so a client can only do
what the content lifecycle allows (approve or request changes while the piece
is in client review).
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext
from django.views import View
from django.views.generic import DetailView, ListView

from accounts.mixins import CapabilityRequiredMixin
from accounts.permissions import Capability
from accounts.roles import Role
from core.actors import actor_for
from core.http import run_action
from production.comments import add_comment
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
        # Only comments written by people with the client role: internal notes stay internal.
        context["client_comments"] = (
            self.object.comments.filter(
                author__memberships__organization=self.object.organization,
                author__memberships__role=Role.CLIENT.value,
            )
            .distinct()
            .order_by("created_at")
        )
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


class PortalCommentView(CapabilityRequiredMixin, View):
    """A client's comment on a piece they can see. Visible to the team and to the client."""

    required_capability = Capability.ACCESS_PORTAL
    http_method_names = ["post"]

    def post(self, request, pk):
        content = get_object_or_404(visible_content(actor_for(request.membership)), pk=pk)
        body = request.POST.get("body", "").strip()
        if not body or len(body) > 2000:
            messages.error(request, gettext("Write a comment of up to 2000 characters."))
        else:
            add_comment(content, request.user, body)
            messages.success(request, gettext("Comment sent."))
        return redirect("portal_detail", pk=pk)
