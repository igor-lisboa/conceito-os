from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from accounts.models import Membership
from accounts.roles import Role
from clients.queries import visible_clients
from core.choices import translated_choices

from .domain.content import Channel, ContentFormat
from .domain.states import ContentState

User = get_user_model()


class ContentVersionForm(forms.Form):
    """The text and media of one version. Used for new versions and inside ContentForm."""

    caption = forms.CharField(label=_("Caption"), widget=forms.Textarea(attrs={"rows": 4}), required=False)
    cta = forms.CharField(label=_("Call to action (CTA)"), max_length=200, required=False)
    script = forms.CharField(label=_("Script"), widget=forms.Textarea(attrs={"rows": 4}), required=False)
    media_url = forms.URLField(label=_("Media link"), max_length=500, required=False)


class ContentForm(ContentVersionForm):
    """Creates a piece together with its first version."""

    field_order = ["client", "title", "channel", "content_format", "owner", "caption", "cta", "script", "media_url"]

    client = forms.ModelChoiceField(queryset=None, label=_("Client"))
    title = forms.CharField(label=_("Title"), max_length=160)
    channel = forms.ChoiceField(label=_("Channel"), choices=translated_choices(Channel))
    content_format = forms.ChoiceField(label=_("Format"), choices=translated_choices(ContentFormat))
    owner = forms.ModelChoiceField(label=_("Responsible"), queryset=None, required=False)

    def __init__(self, *args, membership, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = visible_clients(membership)
        # End customers cannot be responsible for content.
        internal = Membership.objects.filter(organization=membership.organization).exclude(role=Role.CLIENT.value)
        self.fields["owner"].queryset = User.objects.filter(memberships__in=internal).distinct()


class ContentActionForm(forms.Form):
    """Extra input some actions need: a comment or reason, a publishing date, or the link of the post."""

    comment = forms.CharField(label=_("Comment"), widget=forms.Textarea(attrs={"rows": 2}), required=False)
    link = forms.URLField(label=_("Link to the published post"), max_length=500, required=False)
    scheduled_for = forms.DateTimeField(
        label=_("Publish on"),
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )


class ContentStateFilterForm(forms.Form):
    state = forms.ChoiceField(
        label=_("Stage"),
        required=False,
        choices=[("", _("All stages")), *translated_choices(ContentState)],
    )
