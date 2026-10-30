from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        # Importing the module connects the signal receivers.
        from . import signals  # noqa: F401
