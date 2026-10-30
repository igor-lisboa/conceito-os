from .models import Membership

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


class ActiveMembershipMiddleware:
    """Sets request.membership (or None) for every request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.membership = None
        if request.user.is_authenticated:
            request.membership = get_active_membership(request)
        return self.get_response(request)
