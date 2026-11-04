"""Calendar, production board and duplicating a piece (TD-04, TD-05, CAL-004).

Views for planning the work. They reuse visible_content, so what a person sees here
is the same as in the rest of the app.
"""

import calendar
import datetime as dt
from collections import defaultdict

from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.mixins import CapabilityRequiredMixin
from apps.accounts.models import Membership
from apps.accounts.permissions import Capability, has_capability
from apps.clients.queries import visible_clients
from apps.core.actors import actor_for
from apps.core.choices import translated_choices
from apps.core.http import run_action

from .composition import build_content_service
from .domain.content import PLANNED_DATE_OPEN_STATES, Channel, VersionData
from .domain.states import ContentState
from .queries import visible_content


def _month_start(text):
    try:
        year, month = (int(part) for part in text.split("-"))
        return dt.date(year, month, 1)
    except (ValueError, AttributeError):
        return None


def _shift_month(day, months):
    index = day.year * 12 + (day.month - 1) + months
    return dt.date(index // 12, index % 12 + 1, 1)


# Board drag (D-28): each allowed card move and the action the piece page uses for it.
# It is exactly the set of manual moves (PD-41); a test keeps the two in step.
BOARD_DRAG_ACTIONS = {
    (ContentState.DRAFT, ContentState.PLANNED): "plan",
    (ContentState.PLANNED, ContentState.IN_PRODUCTION): "start_production",
    (ContentState.CHANGES_REQUESTED, ContentState.IN_PRODUCTION): "start_production",
    (ContentState.IN_PRODUCTION, ContentState.INTERNAL_REVIEW): "send_internal_review",
}


class PlanningFilterForm(forms.Form):
    """Filters for the calendar and the board (CAL-001). The URL keeps them; an empty field is no filter."""

    client = forms.ModelChoiceField(label=_("Client"), queryset=None, required=False)
    channel = forms.ChoiceField(label=_("Channel"), choices=[], required=False)
    owner = forms.ModelChoiceField(label=_("Owner"), queryset=None, required=False)
    state = forms.ChoiceField(label=_("State"), choices=[], required=False)

    def __init__(self, *args, membership, show_state=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = visible_clients(membership)
        self.fields["channel"].choices = [("", _("All"))] + translated_choices(Channel)
        # Owners are people of this organization only (tenant isolation).
        self.fields["owner"].queryset = get_user_model().objects.filter(
            id__in=Membership.objects.filter(organization=membership.organization).values("user_id")
        )
        if show_state:
            self.fields["state"].choices = [("", _("All"))] + translated_choices(ContentState)
        else:
            del self.fields["state"]

    @property
    def active(self):
        """True when any filter is set, so the filter panel opens (NAV-014)."""
        return any(self.data.get(name) for name in self.fields)

    def apply(self, queryset):
        if not self.is_valid():
            return queryset
        values = self.cleaned_data
        if values.get("client"):
            queryset = queryset.filter(client=values["client"])
        if values.get("channel"):
            queryset = queryset.filter(channel=values["channel"])
        if values.get("owner"):
            queryset = queryset.filter(owner=values["owner"])
        if values.get("state"):
            queryset = queryset.filter(state=values["state"])
        return queryset


class ContentCalendarView(CapabilityRequiredMixin, TemplateView):
    """Scheduled pieces by day. A grid for wide screens and an agenda list for phones."""

    required_capability = Capability.ACCESS_INTERNAL
    template_name = "production/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = self.request.membership
        actor = actor_for(membership)
        filters = PlanningFilterForm(self.request.GET or None, membership=membership, show_state=True)
        month = _month_start(self.request.GET.get("month", "")) or timezone.localdate().replace(day=1)

        # Local time boundaries, so "a day" means the organization's day.
        start = timezone.make_aware(dt.datetime.combine(month, dt.time.min))
        end = timezone.make_aware(dt.datetime.combine(_shift_month(month, 1), dt.time.min))
        scheduled = visible_content(actor).filter(scheduled_for__gte=start, scheduled_for__lt=end)
        # Planned pieces without a schedule yet (PRO-015). Published pieces keep their schedule, so they are excluded.
        planned = visible_content(actor).filter(
            planned_for__gte=start, planned_for__lt=end, scheduled_for__isnull=True
        )
        scheduled = filters.apply(scheduled)
        planned = filters.apply(planned)

        by_day = defaultdict(list)
        for item in scheduled.select_related("client"):
            item.display_at = item.scheduled_for
            item.is_planned = False
            item.can_move = False
            by_day[timezone.localdate(item.display_at)].append(item)
        for item in planned.select_related("client"):
            item.display_at = item.planned_for
            item.is_planned = True
            item.can_move = item.state in PLANNED_DATE_OPEN_STATES
            by_day[timezone.localdate(item.display_at)].append(item)
        for day_items in by_day.values():
            day_items.sort(key=lambda item: item.display_at)

        weeks = [
            [{"date": day, "items": by_day.get(day, []), "in_month": day.month == month.month} for day in week]
            for week in calendar.Calendar(firstweekday=0).monthdatescalendar(month.year, month.month)
        ]
        context.update(
            {
                "filters": filters,
                "month": month,
                "previous_month": _shift_month(month, -1).strftime("%Y-%m"),
                "next_month": _shift_month(month, 1).strftime("%Y-%m"),
                "weeks": weeks,
                "agenda": [(day, by_day[day]) for day in sorted(by_day)],
                "weekday_names": [gettext(name) for name in _weekday_names()],
            }
        )
        return context


def _weekday_names():
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class ContentBoardView(CapabilityRequiredMixin, TemplateView):
    """The production board: one column per stage, cards in each."""

    required_capability = Capability.ACCESS_INTERNAL
    template_name = "production/board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = self.request.membership
        filters = PlanningFilterForm(self.request.GET or None, membership=membership)
        items = filters.apply(visible_content(actor_for(membership)).select_related("client"))
        items = list(items)
        # Dragging a card moves it only along the manual moves (D-28). The page sends the same
        # action the piece page uses, so the server applies the same rule.
        draggable_states = {source.value for source, _target in BOARD_DRAG_ACTIONS}
        can_edit = has_capability(actor_for(membership), Capability.EDIT_CONTENT)
        for item in items:
            item.can_drag = can_edit and item.state in draggable_states
        context["filters"] = filters
        context["drag_moves"] = [
            {"source": source.value, "target": target.value, "action": action}
            for (source, target), action in BOARD_DRAG_ACTIONS.items()
        ]
        context["columns"] = [
            (state, [item for item in items if item.state == state.value]) for state in ContentState
        ]
        return context


class ContentDuplicateView(CapabilityRequiredMixin, View):
    """Start a new draft from the latest text of an existing piece (CAL-004)."""

    required_capability = Capability.CREATE_CONTENT
    http_method_names = ["post"]

    def post(self, request, pk):
        original = get_object_or_404(visible_content(actor_for(request.membership)), pk=pk)
        latest = original.versions.order_by("-number").first()
        result = {}

        def duplicate():
            result["id"] = build_content_service().create(
                actor_for(request.membership),
                client_id=original.client_id,
                title=f"{original.title} ({gettext('copy')})"[:160],
                channel=original.channel,
                content_format=original.content_format,
                owner_id=None,
                version=VersionData(
                    caption=latest.caption,
                    cta=latest.cta,
                    script=latest.script,
                    media_url=latest.media_url,
                ),
            )

        if not run_action(request, duplicate, success_message="Copy created as a draft."):
            return redirect("content_detail", pk=pk)
        return redirect("content_detail", pk=result["id"])
