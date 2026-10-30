from django import forms
from django.utils.translation import gettext_lazy as _


class ClientDecisionForm(forms.Form):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"

    decision = forms.ChoiceField(
        label=_("Decision"),
        choices=[(APPROVE, _("Approve")), (REQUEST_CHANGES, _("Request changes"))],
        widget=forms.RadioSelect,
    )
    comment = forms.CharField(
        label=_("Comment (required when requesting changes)"),
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
    )
