from django import forms
from django.utils.translation import gettext_lazy as _

from .models import BrandAsset, ClientBriefing


class ClientForm(forms.Form):
    """Plain form on purpose: the service function creates the Client, so the
    business rules stay in one place."""

    name = forms.CharField(max_length=120, label=_("Brand name"))
    client_approval_required = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Require client approval before scheduling"),
    )


class ClientBriefingForm(forms.ModelForm):
    class Meta:
        model = ClientBriefing
        fields = ["objective", "audience", "tone_of_voice", "competitors", "notes"]
        labels = {
            "objective": _("Objective"),
            "audience": _("Audience"),
            "tone_of_voice": _("Tone of voice"),
            "competitors": _("Competitors"),
            "notes": _("Notes"),
        }
        widgets = {
            "objective": forms.Textarea(attrs={"rows": 3}),
            "audience": forms.Textarea(attrs={"rows": 3}),
            "tone_of_voice": forms.Textarea(attrs={"rows": 3}),
            "competitors": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class BrandAssetForm(forms.ModelForm):
    class Meta:
        model = BrandAsset
        fields = ["title", "kind", "url"]
        labels = {
            "title": _("Title"),
            "kind": _("Kind"),
            "url": _("Link"),
        }
