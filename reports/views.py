import datetime as dt

from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from accounts.mixins import CapabilityRequiredMixin
from accounts.permissions import Capability
from clients.queries import visible_clients
from core.choices import translated_choices

from .models import EXPECTED_METRICS, Metric, MetricEntry, Platform


def _parse_month(text):
    """Accept YYYY-MM and return the first day of that month, or None."""
    try:
        year, month = (int(part) for part in text.split("-"))
        return dt.date(year, month, 1)
    except (ValueError, AttributeError):
        return None


class MetricEntryForm(forms.Form):
    client = forms.ModelChoiceField(label=_("Client"), queryset=None)
    platform = forms.ChoiceField(label=_("Network"), choices=translated_choices(Platform))
    metric = forms.ChoiceField(label=_("Metric"), choices=translated_choices(Metric))
    month = forms.CharField(label=_("Month"), help_text=_("Format: YYYY-MM"), max_length=7)
    value = forms.IntegerField(label=_("Value"), min_value=0)

    def __init__(self, *args, membership, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = visible_clients(membership)

    def clean_month(self):
        month = _parse_month(self.cleaned_data["month"])
        if month is None:
            raise forms.ValidationError(_("Use the format YYYY-MM, for example 2026-10."))
        return month


class ReportView(CapabilityRequiredMixin, TemplateView):
    """Monthly report for one client: every expected metric, or N/D when nobody entered it."""

    required_capability = Capability.ACCESS_INTERNAL
    template_name = "reports/report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = self.request.membership
        clients = visible_clients(membership)
        client = clients.filter(pk=self.request.GET.get("client")).first() or clients.first()
        month = _parse_month(self.request.GET.get("month", "")) or dt.date.today().replace(day=1)

        rows = []
        if client is not None:
            values = {
                (entry.platform, entry.metric): entry.value
                for entry in MetricEntry.objects.filter(client=client, month=month)
            }
            for platform, metrics in EXPECTED_METRICS.items():
                for metric in metrics:
                    value = values.get((platform, metric.value))
                    rows.append(
                        {
                            "platform": Platform(platform).label,
                            "metric": metric.label,
                            "value": value if value is not None else "N/D",
                            "missing": value is None,
                        }
                    )

        context.update(
            {
                "clients": clients,
                "client": client,
                "month": month,
                "rows": rows,
                "can_enter": self.request.membership.role in ("owner", "account_manager", "creative"),
            }
        )
        return context


class MetricEntryView(CapabilityRequiredMixin, FormView):
    required_capability = Capability.ENTER_METRICS
    template_name = "reports/entry_form.html"
    form_class = MetricEntryForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["membership"] = self.request.membership
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        entry, created = MetricEntry.objects.update_or_create(
            client=data["client"],
            platform=data["platform"],
            metric=data["metric"],
            month=data["month"],
            defaults={
                "organization": self.request.membership.organization,
                "value": data["value"],
                "created_by": self.request.user,
            },
        )
        messages.success(self.request, gettext("Value saved.") if created else gettext("Value updated."))
        return redirect(
            f"{reverse('report')}?client={entry.client_id}&month={entry.month:%Y-%m}"
        )
