from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import View

from . import mfa, throttle
from .middleware import MFA_SESSION_KEY
from .models import MFADevice


class CodeForm(forms.Form):
    code = forms.CharField(label=_("Code from your app"), max_length=8, min_length=6)


def _address(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")


class MFASetupView(LoginRequiredMixin, View):
    """Link an authenticator app. The secret is shown once; the app then produces the codes."""

    template_name = "accounts/mfa_setup.html"

    def get(self, request):
        device = MFADevice.objects.filter(user=request.user).first()
        if device is None or not device.confirmed:
            device, _created = MFADevice.objects.update_or_create(
                user=request.user, defaults={"secret": mfa.new_secret(), "confirmed": False}
            )
        context = {
            "device": device,
            "form": CodeForm(),
            "uri": mfa.provisioning_uri(device.secret, request.user.email) if not device.confirmed else None,
        }
        if context["uri"]:
            context["qr_svg"] = mfa.provisioning_svg(context["uri"])
        return render(request, self.template_name, context)

    def post(self, request):
        device = MFADevice.objects.filter(user=request.user).first()
        if device is None:
            return redirect("mfa_setup")
        form = CodeForm(request.POST)
        if not form.is_valid() or not mfa.verify(device.secret, form.cleaned_data["code"]):
            messages.error(request, gettext("That code is not right. Check the time on your phone and try again."))
            return redirect("mfa_setup")
        device.confirmed = True
        device.save(update_fields=["confirmed"])
        request.session[MFA_SESSION_KEY] = True
        messages.success(request, gettext("Two-step sign-in is on for your account."))
        return redirect("mfa_setup")


class MFAVerifyView(LoginRequiredMixin, View):
    """Asked after the password, once per session, when two-step sign-in is on."""

    template_name = "accounts/mfa_verify.html"

    def get(self, request):
        return render(request, self.template_name, {"form": CodeForm()})

    def post(self, request):
        identifier = f"mfa:{request.user.pk}"
        address = _address(request)
        if throttle.is_locked(identifier, address):
            return render(
                request,
                self.template_name,
                {"form": CodeForm(), "locked": True},
                status=429,
            )

        device = MFADevice.objects.filter(user=request.user, confirmed=True).first()
        form = CodeForm(request.POST)
        if device is None:
            return redirect("home")
        if not form.is_valid() or not mfa.verify(device.secret, form.cleaned_data["code"]):
            throttle.record_failure(identifier, address)
            messages.error(request, gettext("That code is not right."))
            return render(request, self.template_name, {"form": CodeForm()}, status=400)

        throttle.clear_failures(identifier)
        request.session[MFA_SESSION_KEY] = True
        target = request.GET.get("next") or request.POST.get("next") or reverse("home")
        if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
            target = reverse("home")
        return redirect(target)
