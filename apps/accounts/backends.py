from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """Sign in with the email address only (TD-S5 decided 2026-11-16: usernames no longer sign in).

    The class still subclasses ModelBackend so that permission checks (has_perm) keep working.
    Email comparison ignores case, so "Admin@Conceito.com.br" matches the stored address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # The login form's field is called "username" for historical reasons; its value must be an email.
        identifier = username or kwargs.get("email")
        if identifier is None or password is None:
            return None

        user = User.objects.filter(email__iexact=identifier).first()
        if user is None:
            # Hash anyway, so a missing account takes as long as a wrong password.
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
