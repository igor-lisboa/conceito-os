"""A client's campaigns: the list and the form to add one (CAL-001, decided 2026-11-16).

Visibility follows the client wall (SEC-017): a client the person cannot see is "not found".
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext
from django.views import View

from apps.accounts.mixins import CapabilityRequiredMixin
from apps.accounts.permissions import Capability, has_capability

from .forms import CampaignForm
from .models import Campaign
from .queries import visible_clients


class ClientCampaignsView(CapabilityRequiredMixin, View):
    required_capability = Capability.ACCESS_INTERNAL
    template_name = "clients/campaigns.html"

    def get(self, request, pk):
        client_record = get_object_or_404(visible_clients(request.membership), pk=pk)
        return self._render(request, client_record, CampaignForm())

    def post(self, request, pk):
        client_record = get_object_or_404(visible_clients(request.membership), pk=pk)
        if not has_capability(request.membership, Capability.CREATE_CONTENT):
            raise PermissionDenied
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.organization = request.membership.organization
            campaign.client = client_record
            campaign.save()
            messages.success(request, gettext("Campaign created."))
            return redirect("client_campaigns", pk=client_record.pk)
        return self._render(request, client_record, form)

    def _render(self, request, client_record, form):
        campaigns = Campaign.objects.filter(client=client_record)
        return render(
            request,
            self.template_name,
            {"client": client_record, "campaigns": campaigns, "form": form},
        )
