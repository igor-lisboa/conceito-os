"""Calendar, production board and duplicating a piece (TD-04, TD-05, CAL-004).

Views for planning the work. They reuse visible_content, so what a person sees here
is the same as in the rest of the app.
"""

import calendar
import datetime as dt
from collections import defaultdict

from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from accounts.mixins import CapabilityRequiredMixin
from accounts.permissions import Capability
from clients.queries import visible_clients
from core.actors import actor_for
from core.http import run_action

from .composition import build_content_service
from .domain.content import VersionData
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


class PlanningFilterForm(forms.Form):
    client = forms.ModelChoiceField(label=_("Client"), queryset=None, required=False)

    def __init__(self, *args, membership, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = visible_clients(membership)


class ContentCalendarView(CapabilityRequiredMixin, TemplateView):
    """Scheduled pieces by day. A grid for wide screens and an agenda list for phones."""

    required_capability = Capability.ACCESS_INTERNAL
    template_name = "production/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = self.request.membership
        actor = actor_for(membership)
        filters = PlanningFilterForm(self.request.GET or None, membership=membership)
        month = _month_start(self.request.GET.get("month", "")) or timezone.localdate().replace(day=1)

        # Local time boundaries, so "a day" means the organization's day.
        start = timezone.make_aware(dt.datetime.combine(month, dt.time.min))
        end = timezone.make_aware(dt.datetime.combine(_shift_month(month, 1), dt.time.min))
        items = visible_content(actor).filter(scheduled_for__gte=start, scheduled_for__lt=end)
        if filters.is_valid() and filters.cleaned_data.get("client"):
            items = items.filter(client=filters.cleaned_data["client"])
        items = items.select_related("client").order_by("scheduled_for")

        by_day = defaultdict(list)
        for item in items:
            by_day[timezone.localdate(item.scheduled_for)].append(item)

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
        items = visible_content(actor_for(membership)).select_related("client")
        if filters.is_valid() and filters.cleaned_data.get("client"):
            items = items.filter(client=filters.cleaned_data["client"])
        items = list(items)
        context["filters"] = filters
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
