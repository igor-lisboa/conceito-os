"""Client portal sections beyond approvals: calendar, results, files and contact (TD-26, POR-002).

Each one shows only what belongs to the client's own brands. Nothing internal:
no margins, no other clients, no internal notes.
"""

import datetime as dt
from collections import defaultdict

from django.conf import settings
from django.utils import timezone
from django.views.generic import TemplateView

from apps.accounts.mixins import CapabilityRequiredMixin
from apps.accounts.permissions import Capability
from apps.clients.models import BrandAsset
from apps.clients.queries import visible_clients
from apps.core.actors import actor_for
from apps.production.queries import visible_content
from apps.reports.models import EXPECTED_METRICS, MetricEntry, Platform


class PortalCalendarView(CapabilityRequiredMixin, TemplateView):
    required_capability = Capability.ACCESS_PORTAL
    template_name = "portal/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        items = (
            visible_content(actor_for(self.request.membership))
            .filter(scheduled_for__isnull=False, scheduled_for__gte=timezone.now() - dt.timedelta(days=1))
            .select_related("client")
            .order_by("scheduled_for")
        )
        by_day = defaultdict(list)
        for item in items:
            by_day[timezone.localdate(item.scheduled_for)].append(item)
        context.update({"today": today, "agenda": [(day, by_day[day]) for day in sorted(by_day)]})
        return context


class PortalResultsView(CapabilityRequiredMixin, TemplateView):
    """Monthly figures entered by the team for the client's brands. Missing values show as N/D."""

    required_capability = Capability.ACCESS_PORTAL
    template_name = "portal/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = timezone.localdate().replace(day=1)
        blocks = []
        for client in visible_clients(self.request.membership):
            values = {
                (entry.platform, entry.metric): entry.value
                for entry in MetricEntry.objects.filter(client=client, month=month)
            }
            rows = []
            for platform, metrics in EXPECTED_METRICS.items():
                for metric in metrics:
                    value = values.get((platform, metric.value))
                    rows.append(
                        {
                            "platform": Platform(platform).label,
                            "metric": metric.label,
                            "value": value if value is not None else "N/D",
                        }
                    )
            blocks.append({"client": client, "rows": rows})
        context.update({"month": month, "blocks": blocks})
        return context


class PortalFilesView(CapabilityRequiredMixin, TemplateView):
    required_capability = Capability.ACCESS_PORTAL
    template_name = "portal/files.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assets = BrandAsset.objects.filter(
            organization=self.request.membership.organization,
            client__in=visible_clients(self.request.membership),
        ).select_related("client")
        context["assets"] = assets
        return context


class PortalContactView(CapabilityRequiredMixin, TemplateView):
    required_capability = Capability.ACCESS_PORTAL
    template_name = "portal/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_email"] = settings.CONTACT_EMAIL
        return context
