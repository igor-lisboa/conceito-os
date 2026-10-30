"""Errors the application core can raise. They are plain Python classes.

Adapters (views, the Django layer) turn them into HTTP answers, see core/http.py.
Keeping them free of Django lets domain and application code raise them freely.
"""


class DomainError(Exception):
    """A business rule stopped the action, for example an invalid state change.

    `message` is an English message identifier (msgid). The web layer translates
    it with gettext, so the domain never imports Django. Placeholders such as
    {source} are filled from `params`, and translated too when they are labels.
    """

    def __init__(self, message, **params):
        self.message = message
        self.params = params
        super().__init__(message.format(**params))


class Forbidden(Exception):
    """The actor's role does not allow this action (HTTP 403)."""


class NotFound(Exception):
    """The record does not exist OR is outside the actor's scope (HTTP 404).

    Both cases look the same on purpose, so an attacker cannot discover which
    IDs exist in another organization or client.
    """
