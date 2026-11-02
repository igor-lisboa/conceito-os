from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views import View
from django.views.generic import FormView, ListView, UpdateView

from apps.accounts.mixins import CapabilityRequiredMixin
from apps.accounts.permissions import Capability
from apps.core.http import run_action

from . import team, throttle
from .forms import AccountLanguageForm, EmailAuthenticationForm, InviteMemberForm, OrganizationForm
from .models import Membership


class ThrottledLoginView(auth_views.LoginView):
    """The sign-in page, with a limit on failed attempts (SEC-008)."""

    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm

    def post(self, request, *args, **kwargs):
        identifier = request.POST.get("username", "").strip().lower()
        address = _client_address(request)
        if throttle.is_locked(identifier, address):
            form = self.get_form()
            form.add_error(None, gettext("Too many failed attempts. Try again in 15 minutes."))
            return self.render_to_response(self.get_context_data(form=form), status=429)

        response = super().post(request, *args, **kwargs)
        if request.user.is_authenticated:
            throttle.clear_failures(identifier)
        else:
            throttle.record_failure(identifier, address)
        return response


def _client_address(request):
    # Behind Vercel the first address in X-Forwarded-For is the client's.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")


class TeamListView(CapabilityRequiredMixin, ListView):
    required_capability = Capability.MANAGE_TEAM
    template_name = "accounts/team_list.html"
    context_object_name = "members"

    def get_queryset(self):
        return (
            Membership.objects.filter(organization=self.request.membership.organization)
            .select_related("user")
            .prefetch_related("client_accesses__client")
        )


class TeamInviteView(CapabilityRequiredMixin, FormView):
    required_capability = Capability.MANAGE_TEAM
    template_name = "accounts/team_invite.html"
    form_class = InviteMemberForm
    success_url = reverse_lazy("team_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["membership"] = self.request.membership
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        created = run_action(
            self.request,
            lambda: team.invite_member(
                self.request.membership,
                email=data["email"],
                role=data["role"],
                client_ids=[client.pk for client in data["clients"]],
            ),
            success_message="Invitation sent.",
        )
        return super().form_valid(form) if created else self.form_invalid(form)


class TeamRemoveView(CapabilityRequiredMixin, View):
    required_capability = Capability.MANAGE_TEAM
    http_method_names = ["post"]

    def post(self, request, pk):
        target = get_object_or_404(Membership, pk=pk, organization=request.membership.organization)
        run_action(
            request,
            lambda: team.remove_member(request.membership, target),
            success_message="Access removed.",
        )
        return redirect("team_list")


class AccountView(LoginRequiredMixin, UpdateView):
    """Each person's own settings. Any role can change its own email language (NTF-010)."""

    template_name = "accounts/account.html"
    form_class = AccountLanguageForm
    success_url = reverse_lazy("account")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, gettext("Settings saved."))
        return super().form_valid(form)


class OrganizationSettingsView(CapabilityRequiredMixin, UpdateView):
    required_capability = Capability.MANAGE_TEAM
    template_name = "accounts/organization_settings.html"
    form_class = OrganizationForm
    success_url = reverse_lazy("organization_settings")

    def get_object(self, queryset=None):
        return self.request.membership.organization

    def form_valid(self, form):
        messages.success(self.request, gettext("Settings saved."))
        return super().form_valid(form)
