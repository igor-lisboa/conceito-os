from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView

from apps.accounts.mixins import CapabilityRequiredMixin
from apps.accounts.models import Role
from apps.accounts.permissions import Capability
from apps.production.domain.states import ContentState
from apps.production.queries import visible_content

from .actors import actor_for
from .models import AuditEvent


class HomeView(LoginRequiredMixin, View):
    """Client users go to their portal; everyone else gets the internal dashboard."""

    def get(self, request):
        membership = request.membership
        if membership is None:
            return render(request, "core/no_organization.html", status=403)
        if membership.role == Role.CLIENT:
            return redirect("portal_list")

        content = visible_content(actor_for(membership))
        counts = {
            "internal_review": content.filter(state=ContentState.INTERNAL_REVIEW).count(),
            "client_review": content.filter(state=ContentState.CLIENT_REVIEW).count(),
            "scheduled": content.filter(state=ContentState.SCHEDULED).count(),
            "failed": content.filter(state=ContentState.FAILED).count(),
        }
        return render(request, "core/dashboard.html", {"counts": counts})


class AuditLogView(CapabilityRequiredMixin, ListView):
    """What happened in the organization, newest first. Owners only (AUTH-020)."""

    required_capability = Capability.VIEW_AUDIT
    template_name = "core/audit.html"
    context_object_name = "events"
    paginate_by = 50

    def get_queryset(self):
        queryset = AuditEvent.objects.filter(organization=self.request.membership.organization).select_related(
            "actor"
        )
        action = self.request.GET.get("action", "").strip()
        if action:
            queryset = queryset.filter(action__startswith=action)
        return queryset
