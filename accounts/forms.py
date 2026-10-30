from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class EmailAuthenticationForm(AuthenticationForm):
    """Login form that asks for an email address (the username still works)."""

    username = forms.CharField(label=_("Email"), widget=forms.TextInput(attrs={"autofocus": True}))
