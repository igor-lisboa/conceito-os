from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import Membership, MFADevice

ACTIVE_MEMBERSHIP_SESSION_KEY = "active_membership_id"


def get_active_membership(request):
    """Return the membership the user is working in.

    A user with several organizations picks one; we remember the choice in the
    session. Without a valid choice we use their first membership.
    """
    memberships = list(Membership.objects.select_related("organization").filter(user=request.user))
    if not memberships:
        return None

    chosen_id = request.session.get(ACTIVE_MEMBERSHIP_SESSION_KEY)
    for membership in memberships:
        if membership.id == chosen_id:
            return membership
    return memberships[0]


class OrganizationTimezoneMiddleware:
    """Show and enter dates in the active organization's time zone.

    Times are stored in UTC; this only changes how they are displayed and typed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        membership = getattr(request, "membership", None)
        if membership is None:
            timezone.deactivate()
        else:
            try:
                timezone.activate(ZoneInfo(membership.organization.timezone))
            except (ZoneInfoNotFoundError, ValueError):
                timezone.activate(ZoneInfo("UTC"))
        return self.get_response(request)


class ActiveMembershipMiddleware:
    """Sets request.membership (or None) for every request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.membership = None
        if request.user.is_authenticated:
            request.membership = get_active_membership(request)
        return self.get_response(request)


MFA_SESSION_KEY = "mfa_verified"
MFA_EXEMPT_PREFIXES = ("/accounts/mfa/", "/accounts/logout/", "/i18n/", "/static/")


class MFAEnforcementMiddleware:
    """After the password, people with two-step sign-in on must enter a code once per session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and not request.session.get(MFA_SESSION_KEY)
            and not request.path.startswith(MFA_EXEMPT_PREFIXES)
        ):
            if MFADevice.objects.filter(user=user, confirmed=True).exists():
                return redirect(f"{reverse('mfa_verify')}?next={request.get_full_path()}")
        return self.get_response(request)
