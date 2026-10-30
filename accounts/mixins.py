from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .permissions import has_capability


class CapabilityRequiredMixin(LoginRequiredMixin):
    """Use on a view to require a logged-in user whose role grants `required_capability`.

    Anonymous users are sent to the login page. Logged-in users without the
    capability get HTTP 403.
    """

    required_capability = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not has_capability(request.membership, self.required_capability):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
