"""End a person's open sessions (AUTH-003, AUTH-012).

Sessions live in the database (the Django default). Removing someone's access
must end their signed-in browsers at once, so a later re-invitation does not
reopen an old session. Django checks the password hash on every request, which
already covers password changes.
"""

from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.models import Session
from django.utils import timezone


def end_user_sessions(user):
    """Delete every unexpired database session that belongs to `user`. Returns how many were ended."""
    user_key = str(user.pk)
    ended = []
    for session in Session.objects.filter(expire_date__gt=timezone.now()).only("session_key", "session_data"):
        if str(session.get_decoded().get(SESSION_KEY)) == user_key:
            ended.append(session.session_key)
    if ended:
        Session.objects.filter(session_key__in=ended).delete()
    return len(ended)
