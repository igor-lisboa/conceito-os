from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Sign in with the email address (the normal way) or with the username.

    Email comparison ignores case, so "Admin@Conceito.com.br" matches the stored address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get("email")
        if identifier is None or password is None:
            return None

        user = User.objects.filter(email__iexact=identifier).first() or User.objects.filter(
            username=identifier
        ).first()
        if user is None:
            # Hash anyway, so a missing account takes as long as a wrong password.
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
