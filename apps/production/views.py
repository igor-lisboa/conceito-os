"""Web layer for internal users. Views translate HTTP into service calls and back.

They hold no business rules: they read the form, call ContentService, and show
the result. Errors are translated by core/http.py.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext
from django.views import View
from django.views.generic import DetailView, FormView, ListView

from apps.accounts.mixins import CapabilityRequiredMixin
from apps.accounts.permissions import Capability, has_capability
from apps.core.actors import actor_for
from apps.core.http import run_action

from .comments import add_comment
from .composition import build_content_service
from .domain.content import PLANNED_DATE_OPEN_STATES, VersionData
from .domain.states import ContentState
from .forms import (
    ContentActionForm,
    ContentForm,
    ContentStateFilterForm,
    ContentVersionForm,
    PlannedDateForm,
)
from .queries import visible_content


def _available_actions(actor, state):
    """Which buttons to show. A convenience only: the service enforces the same rules."""
    can_edit = has_capability(actor, Capability.EDIT_CONTENT)
    can_approve = has_capability(actor, Capability.APPROVE_INTERNAL)
    can_schedule = has_capability(actor, Capability.SCHEDULE_CONTENT)
    return {
        "plan": can_edit and state == ContentState.DRAFT,
        "start_production": can_edit and state in (ContentState.PLANNED, ContentState.CHANGES_REQUESTED),
        "send_internal_review": can_edit and state == ContentState.IN_PRODUCTION,
        "approve_internal": can_approve and state == ContentState.INTERNAL_REVIEW,
        "reject_internal": can_approve and state == ContentState.INTERNAL_REVIEW,
        "schedule": can_schedule and state in (ContentState.APPROVED, ContentState.FAILED),
        "unschedule": can_schedule and state == ContentState.SCHEDULED,
        "mark_published": can_schedule and state == ContentState.SCHEDULED,
        "mark_failed": can_schedule and state == ContentState.SCHEDULED,
        "reschedule": can_edit and state in PLANNED_DATE_OPEN_STATES,
    }


class ContentListView(CapabilityRequiredMixin, ListView):
    required_capability = Capability.ACCESS_INTERNAL
    template_name = "production/content_list.html"
    context_object_name = "items"

    def get_queryset(self):
        queryset = visible_content(actor_for(self.request.membership)).select_related("client")
        self.filter_form = ContentStateFilterForm(self.request.GET or None)
        if self.filter_form.is_valid() and self.filter_form.cleaned_data["state"]:
            queryset = queryset.filter(state=self.filter_form.cleaned_data["state"])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context


class ContentCreateView(CapabilityRequiredMixin, FormView):
    required_capability = Capability.CREATE_CONTENT
    template_name = "production/content_form.html"
    form_class = ContentForm
    success_url = reverse_lazy("content_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["membership"] = self.request.membership
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        owner = data["owner"]
        created = run_action(
            self.request,
            lambda: build_content_service().create(
                actor_for(self.request.membership),
                client_id=data["client"].pk,
                title=data["title"],
                channel=data["channel"],
                content_format=data["content_format"],
                owner_id=owner.pk if owner else None,
                version=VersionData(
                    caption=data["caption"],
                    cta=data["cta"],
                    script=data["script"],
                    media_url=data["media_url"],
                ),
            ),
            success_message="Content created.",
        )
        return super().form_valid(form) if created else self.form_invalid(form)


class ContentDetailView(CapabilityRequiredMixin, DetailView):
    required_capability = Capability.ACCESS_INTERNAL
    template_name = "production/content_detail.html"

    def get_queryset(self):
        return visible_content(actor_for(self.request.membership)).select_related("client", "owner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest = self.object.versions.order_by("-number").first()
        context["latest"] = latest
        context["versions"] = self.object.versions.all()
        context["approvals"] = self.object.approvals.select_related("version", "actor")
        context["version_form"] = ContentVersionForm(
            initial={
                "caption": latest.caption,
                "cta": latest.cta,
                "script": latest.script,
                "media_url": latest.media_url,
            }
        )
        context["action_form"] = ContentActionForm()
        context["planned_form"] = PlannedDateForm(initial={"planned_for": self.object.planned_for})
        context["comments"] = self.object.comments.select_related("author")
        context["actions"] = _available_actions(actor_for(self.request.membership), self.object.state)
        return context


class ContentVersionView(CapabilityRequiredMixin, View):
    """Receives the form that saves a new version of a piece."""

    required_capability = Capability.EDIT_CONTENT
    http_method_names = ["post"]

    def post(self, request, pk):
        form = ContentVersionForm(request.POST)
        if not form.is_valid():
            messages.error(request, gettext("Check the version fields."))
        else:
            run_action(
                request,
                lambda: build_content_service().add_version(
                    actor_for(request.membership), pk, VersionData(**form.cleaned_data)
                ),
                success_message="New version saved.",
            )
        return redirect("content_detail", pk=pk)


# Each action name maps to one service call. The URL is /conteudos/<pk>/acao/<name>/
ACTION_HANDLERS = {
    "plan": lambda s, a, i, d: s.move_to(a, i, ContentState.PLANNED),
    "start_production": lambda s, a, i, d: s.move_to(a, i, ContentState.IN_PRODUCTION),
    "send_internal_review": lambda s, a, i, d: s.move_to(a, i, ContentState.INTERNAL_REVIEW),
    "approve_internal": lambda s, a, i, d: s.decide_internal(a, i, approve=True, comment=d["comment"]),
    "reject_internal": lambda s, a, i, d: s.decide_internal(a, i, approve=False, comment=d["comment"]),
    "schedule": lambda s, a, i, d: s.schedule(a, i, when=d["scheduled_for"]),
    "unschedule": lambda s, a, i, d: s.unschedule(a, i),
    "mark_published": lambda s, a, i, d: s.mark_published(a, i, url=d["link"]),
    "mark_failed": lambda s, a, i, d: s.mark_failed(a, i, reason=d["comment"]),
}


class ContentActionView(CapabilityRequiredMixin, View):
    required_capability = Capability.ACCESS_INTERNAL
    http_method_names = ["post"]

    def post(self, request, pk, action):
        handler = ACTION_HANDLERS.get(action)
        if handler is None:
            raise Http404("Unknown action.")

        form = ContentActionForm(request.POST)
        if not form.is_valid():
            messages.error(request, gettext("Check the fields you entered."))
        else:
            run_action(
                request,
                lambda: handler(build_content_service(), actor_for(request.membership), pk, form.cleaned_data),
                success_message="Action recorded.",
            )
        # The board sends "next" when a card is dragged, so the person stays on the board.
        next_url = request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("content_detail", pk=pk)


class ContentRescheduleView(CapabilityRequiredMixin, View):
    """Changes the planned date of a piece. Used by the form on the piece and by drag on the calendar (PRO-015)."""

    required_capability = Capability.EDIT_CONTENT
    http_method_names = ["post"]

    def post(self, request, pk):
        form = PlannedDateForm(request.POST)
        if not form.is_valid():
            messages.error(request, gettext("Check the date and the reason."))
        else:
            run_action(
                request,
                lambda: build_content_service().reschedule(
                    actor_for(request.membership),
                    pk,
                    when=form.cleaned_data["planned_for"],
                    reason=form.cleaned_data["reason"],
                ),
                success_message="Planned date changed.",
            )
        return redirect("content_detail", pk=pk)


class ContentCommentView(CapabilityRequiredMixin, View):
    """A team comment on a piece. Mentioned members are notified (PRO-004, NTF-006)."""

    required_capability = Capability.ACCESS_INTERNAL
    http_method_names = ["post"]

    def post(self, request, pk):
        content = get_object_or_404(visible_content(actor_for(request.membership)), pk=pk)
        body = request.POST.get("body", "").strip()
        if not body or len(body) > 2000:
            messages.error(request, gettext("Write a comment of up to 2000 characters."))
        else:
            add_comment(content, request.user, body)
            messages.success(request, gettext("Comment added."))
        return redirect("content_detail", pk=pk)
