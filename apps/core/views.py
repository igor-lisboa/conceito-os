from urllib.parse import quote, urlencode

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import FormView, ListView, TemplateView

from apps.accounts.mixins import CapabilityRequiredMixin
from apps.accounts.models import Role
from apps.accounts.permissions import Capability
from apps.production.domain.states import ContentState
from apps.production.queries import visible_content

from .actors import actor_for
from .forms import ContactForm
from .models import AuditEvent


class LandingView(TemplateView):
    template_name = "core/landing.html"
    extra_context = {"public_page": True}


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm
    extra_context = {"public_page": True}

    def form_valid(self, form):
        data = form.cleaned_data
        interest = dict(form.fields["interest"].choices)[data["interest"]]
        body = "\n".join([
            _("Your name") + ": " + data["name"],
            _("Your email") + ": " + data["email"],
            _("Company or brand") + ": " + data["company"],
            _("How can we help?") + ": " + str(interest),
            "", data["message"],
        ])
        query = urlencode({
            "subject": _("Let's talk about your project") + " · " + data["company"],
            "body": body,
        }, quote_via=quote)
        mailto = "mailto:" + quote(settings.CONTACT_EMAIL, safe="@.") + "?" + query
        return self.render_to_response(self.get_context_data(
            form=form, mailto=mailto, contact_email=settings.CONTACT_EMAIL, interest_label=interest,
        ))


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
