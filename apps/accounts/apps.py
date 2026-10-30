from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "apps.accounts"

    def ready(self):
        # Importing the module connects the signal receivers.
        from . import signals  # noqa: F401
