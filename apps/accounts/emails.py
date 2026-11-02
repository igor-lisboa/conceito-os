"""Emails sent by the accounts app: the welcome message for new users.

Password recovery emails are sent by Django's built-in views (see accounts/urls.py).
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation

logger = logging.getLogger(__name__)

# The team is Brazilian, so the welcome email is written in pt-BR when the person has not chosen a
# language yet (TD-S2, NTF-010). A new account has no choice yet, so it gets this default.
WELCOME_EMAIL_LANGUAGE = "pt-br"


def send_welcome_email(user):
    """Send the welcome message. Failures are logged, not raised: a broken mail server
    must not break creating the account."""
    with translation.override(user.language or WELCOME_EMAIL_LANGUAGE):
        context = {
            "user": user,
            "login_url": f"{settings.SITE_URL}{reverse('login')}",
        }
        subject = render_to_string("emails/welcome_subject.txt", context).strip()
        body = render_to_string("emails/welcome.txt", context)

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
    except Exception:
        logger.exception("Could not send the welcome email to user %s", user.pk)
