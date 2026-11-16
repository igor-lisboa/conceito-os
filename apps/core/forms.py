from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    """A public inquiry. Answers go into a mail draft, never into a database."""

    name = forms.CharField(
        label=_("Your name"), max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label=_("Your email"), widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    company = forms.CharField(
        label=_("Company or brand"), max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "organization"}),
    )
    interest = forms.ChoiceField(
        label=_("How can we help?"), choices=[
            ("", _("Select an option")),
            ("social", _("Social media management")),
            ("content", _("Content planning and production")),
            ("platform", _("Conceito OS for my team")),
            ("other", _("Something else")),
        ],
    )
    message = forms.CharField(
        label=_("Tell us a little about your project"), max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
