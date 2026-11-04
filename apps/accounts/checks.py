"""System checks for the accounts app.

Production must have the MFA encryption key (TD-S11). Without it the sign-in
for owners and administrators with MFA cannot work, so the check fails early,
at deploy and migrate time, instead of at a user's first sign-in.
"""

from django.conf import settings
from django.core.checks import Error, register


@register("deployment")
def check_mfa_encryption_key(app_configs, **kwargs):
    if settings.DEBUG or getattr(settings, "MFA_ENCRYPTION_KEY", ""):
        return []
    return [
        Error(
            "MFA_ENCRYPTION_KEY is not set.",
            hint="Set it in the hosting settings. Generate one with "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\".",
            id="accounts.E001",
        )
    ]
