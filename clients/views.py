from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from accounts.mixins import CapabilityRequiredMixin
from accounts.permissions import Capability
from core.actors import actor_for
from core.http import run_action
from production.queries import visible_content

from . import services
from .forms import BrandAssetForm, ClientBriefingForm, ClientForm
from .queries import visible_clients


class ClientListView(CapabilityRequiredMixin, ListView):
    required_capability = Capability.ACCESS_INTERNAL
    template_name = "clients/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return visible_clients(self.request.membership)


class ClientCreateView(CapabilityRequiredMixin, FormView):
    required_capability = Capability.CREATE_CLIENT
    template_name = "clients/client_form.html"
    form_class = ClientForm
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        created = run_action(
            self.request,
            lambda: services.create_client(
                self.request.membership,
                name=form.cleaned_data["name"],
                client_approval_required=form.cleaned_data["client_approval_required"],
            ),
            success_message="Client created.",
        )
        return super().form_valid(form) if created else self.form_invalid(form)


class ClientDetailView(CapabilityRequiredMixin, DetailView):
    required_capability = Capability.ACCESS_INTERNAL
    template_name = "clients/client_detail.html"

    def get_queryset(self):
        return visible_clients(self.request.membership)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content_items"] = visible_content(actor_for(self.request.membership)).filter(client=self.object)
        return context


class BriefingUpdateView(CapabilityRequiredMixin, UpdateView):
    required_capability = Capability.EDIT_BRIEFING
    template_name = "clients/briefing_form.html"
    form_class = ClientBriefingForm

    def get_object(self, queryset=None):
        # Out-of-scope clients get 404, the same as clients that do not exist.
        client = get_object_or_404(visible_clients(self.request.membership), pk=self.kwargs["pk"])
        return client.briefing

    def form_valid(self, form):
        # Saving goes through the service so the change is audited.
        saved = run_action(
            self.request,
            lambda: services.update_briefing(self.request.membership, self.object.client, **form.cleaned_data),
            success_message="Briefing saved.",
        )
        if not saved:
            return self.form_invalid(form)
        return redirect("client_detail", pk=self.object.client_id)


class AssetCreateView(CapabilityRequiredMixin, CreateView):
    """Add a link to the brand library (CLI-007). Files stay where they are."""

    required_capability = Capability.EDIT_BRIEFING
    template_name = "clients/asset_form.html"
    form_class = BrandAssetForm

    def dispatch(self, request, *args, **kwargs):
        # Out-of-scope clients get 404 before any form work.
        if request.user.is_authenticated:
            self.client_record = get_object_or_404(visible_clients(request.membership), pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(client_record=self.client_record, **kwargs)

    def form_valid(self, form):
        form.instance.organization = self.request.membership.organization
        form.instance.client = self.client_record
        messages.success(self.request, gettext("Link added to the library."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("client_detail", args=[self.client_record.pk])
