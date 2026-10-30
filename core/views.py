from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from accounts.models import Role
from production.domain.states import ContentState
from production.queries import visible_content

from .actors import actor_for


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
