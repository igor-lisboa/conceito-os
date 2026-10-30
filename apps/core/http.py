from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import gettext

from apps.core.exceptions import DomainError, Forbidden, NotFound


def translated_message(error):
    """The user-facing text of a DomainError, in the active language."""
    params = {
        name: gettext(value) if isinstance(value, str) else value
        for name, value in error.params.items()
    }
    return gettext(error.message).format(**params)


def run_action(request, action, success_message=None):
    """Run one application action from a view and translate its errors.

    - Forbidden -> HTTP 403
    - NotFound  -> HTTP 404
    - DomainError -> a translated message to the user, nothing is lost
    Returns True when the action succeeded.
    """
    try:
        action()
    except Forbidden as error:
        raise PermissionDenied(str(error)) from error
    except NotFound:
        raise Http404("Not found.") from None
    except DomainError as error:
        messages.error(request, translated_message(error))
        return False

    if success_message:
        messages.success(request, gettext(success_message))
    return True
