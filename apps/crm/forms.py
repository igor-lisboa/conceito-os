from django import forms
from django.utils.translation import gettext_lazy as _

from apps.clients.queries import visible_clients
from apps.core.choices import translated_choices

from .models import Lead, LeadSource, LeadStage, Proposal, ProposalStatus


class LeadForm(forms.ModelForm):
    source = forms.ChoiceField(label=_("Source"), choices=translated_choices(LeadSource))
    stage = forms.ChoiceField(label=_("Stage"), choices=translated_choices(LeadStage), initial=LeadStage.NEW.value)

    class Meta:
        model = Lead
        fields = ["name", "source", "stage", "contact", "next_action", "next_action_date", "notes"]
        labels = {
            "name": _("Name"),
            "contact": _("Contact"),
            "next_action": _("Next action"),
            "next_action_date": _("Next action date"),
            "notes": _("Notes"),
        }
        widgets = {
            "next_action_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ProposalForm(forms.ModelForm):
    status = forms.ChoiceField(label=_("Status"), choices=translated_choices(ProposalStatus))
    lead = forms.ModelChoiceField(label=_("Lead"), queryset=None, required=False)
    client = forms.ModelChoiceField(label=_("Client"), queryset=None, required=False)

    class Meta:
        model = Proposal
        fields = ["title", "amount", "status", "lead", "client"]
        labels = {"title": _("Title"), "amount": _("Amount (BRL)")}

    def __init__(self, *args, membership, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lead"].queryset = Lead.objects.filter(organization=membership.organization)
        self.fields["client"].queryset = visible_clients(membership)
