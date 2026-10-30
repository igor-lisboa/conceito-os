"""Django edge helper: turns a LabeledEnum into translatable field choices.

The enum labels are English identifiers. gettext_lazy translates them at the
moment they are displayed, so the same database value shows in the language of
the current request.
"""

from django.utils.translation import gettext_lazy


def translated_choices(enum_class):
    return [(member.value, gettext_lazy(member.label)) for member in enum_class]
