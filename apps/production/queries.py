"""Read side: lists and counts for screens.

Reads use the ORM directly. That is a deliberate shortcut: a list does not need
the full aggregate, and rebuilding every piece just to show a table would be
slow. Writes always go through production/application/content_service.py.

The visibility rule itself lives in production/domain/policy.py (Scope). This module
only applies it as a database filter.
"""

from .domain.policy import Scope
from .models import ContentItem


def visible_content(actor):
    return Scope.of(actor).filter_queryset(ContentItem.objects.all())
