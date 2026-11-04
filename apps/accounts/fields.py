"""Encryption at rest for the MFA secret (TD-S11, AUTH-004, SEC-005).

The authenticator secret is a shared key: anyone who reads it can produce valid
codes. It is stored as a Fernet token (AES-128-CBC with HMAC-SHA256), with a key
that lives outside the database, in the MFA_ENCRYPTION_KEY environment variable.

Code always works with the plain secret; the field encrypts on write and decrypts
on read, so no caller has to remember to do it.
"""

import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

# Every Fernet token starts with this prefix (version byte 0x80 in base64).
TOKEN_PREFIX = "gAAAAA"


def _resolve_key():
    key = getattr(settings, "MFA_ENCRYPTION_KEY", "")
    if key:
        return key.encode("ascii")
    if settings.DEBUG:
        # Local development only: derive a stable key from SECRET_KEY so the app runs
        # without extra setup. Production must set MFA_ENCRYPTION_KEY explicitly.
        digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)
    raise ImproperlyConfigured(
        "MFA_ENCRYPTION_KEY is not set. Generate one with: "
        'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
    )


@lru_cache(maxsize=4)
def _fernet_for(key):
    return Fernet(key)


def encrypt_secret(plain):
    return _fernet_for(_resolve_key()).encrypt(plain.encode("ascii")).decode("ascii")


def decrypt_secret(token):
    try:
        return _fernet_for(_resolve_key()).decrypt(token.encode("ascii")).decode("ascii")
    except InvalidToken as error:
        # Never return the ciphertext as if it were a secret: that would give wrong codes silently.
        raise ValueError("MFA secret cannot be decrypted; check MFA_ENCRYPTION_KEY") from error


def is_encrypted(value):
    return value.startswith(TOKEN_PREFIX)


class EncryptedSecretField(models.CharField):
    """A CharField whose value is encrypted in the database and plain in Python."""

    description = "Text encrypted at rest with MFA_ENCRYPTION_KEY"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_secret(value)

    def to_python(self, value):
        # Values from forms or fixtures are plain; values already encrypted are never re-encrypted here.
        return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        return encrypt_secret(value)
