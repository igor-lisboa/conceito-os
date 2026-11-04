"""Two-step sign-in with an authenticator app (AUTH-004). TOTP as in RFC 6238.

Works with Google Authenticator, Microsoft Authenticator, 1Password and similar apps.
Uses the Python standard library for the codes; `qrcode` only draws the setup QR code (TD-S12).
"""

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

import qrcode
import qrcode.image.svg

STEP_SECONDS = 30
DIGITS = 6
WINDOW_STEPS = 1  # accept the previous and next 30-second code, for clock drift


def new_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _code_at(secret, counter):
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    number = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(number % (10**DIGITS)).zfill(DIGITS)


def verify(secret, code, now=None):
    """True if `code` is valid for `secret` now (within one step of drift)."""
    code = (code or "").replace(" ", "")
    if not (code.isdigit() and len(code) == DIGITS):
        return False
    counter = int((now if now is not None else time.time()) // STEP_SECONDS)
    matches = [
        hmac.compare_digest(_code_at(secret, counter + step), code)
        for step in range(-WINDOW_STEPS, WINDOW_STEPS + 1)
    ]
    return any(matches)


def provisioning_uri(secret, account_email, issuer="Conceito OS"):
    label = quote(f"{issuer}:{account_email}")
    return f"otpauth://totp/{label}?secret={secret}&issuer={quote(issuer)}&digits={DIGITS}&period={STEP_SECONDS}"


def provisioning_svg(uri):
    """The setup link as an inline SVG QR code (TD-S12). Built only from our own link, so it is safe to embed."""
    image = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage, box_size=8, border=2)
    return image.to_string(encoding="unicode")
