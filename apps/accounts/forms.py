from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from apps.clients.queries import visible_clients
from apps.core.choices import translated_choices

from .models import Organization
from .roles import Role

# Time zones offered in the settings screen. Brazil spans several; UTC is for tests and exports.
TIMEZONE_CHOICES = [
    ("America/Sao_Paulo", "Brasília (São Paulo, Rio, Belo Horizonte)"),
    ("America/Manaus", "Manaus"),
    ("America/Cuiaba", "Cuiabá"),
    ("America/Fortaleza", "Fortaleza, Salvador, Recife"),
    ("America/Belem", "Belém"),
    ("America/Rio_Branco", "Rio Branco"),
    ("America/Noronha", "Fernando de Noronha"),
    ("UTC", "UTC"),
]


class EmailAuthenticationForm(AuthenticationForm):
    """Login form that asks for an email address (the username still works)."""

    username = forms.CharField(label=_("Email"), widget=forms.TextInput(attrs={"autofocus": True}))


class InviteMemberForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)
    role = forms.ChoiceField(label=_("Role"), choices=translated_choices(Role))
    clients = forms.ModelMultipleChoiceField(
        label=_("Clients this person can see"),
        queryset=None,
        required=False,
        help_text=_("Owners see every client, so this is only needed for other roles."),
    )

    def __init__(self, *args, membership, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["clients"].queryset = visible_clients(membership)


class OrganizationForm(forms.ModelForm):
    timezone = forms.ChoiceField(label=_("Time zone"), choices=TIMEZONE_CHOICES)

    class Meta:
        model = Organization
        fields = ["name", "timezone"]
        labels = {"name": _("Organization name")}
