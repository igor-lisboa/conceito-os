"""Read side: lists and counts for screens.

Reads use the ORM directly. That is a deliberate shortcut: a list does not need
the full aggregate, and rebuilding every piece just to show a table would be
slow. Writes always go through production/application/content_service.py.

The filter below must match production/domain/policy.py. tests/test_queries.py
checks that both agree.
"""

from .models import ContentItem


def visible_content(actor):
    queryset = ContentItem.objects.filter(organization_id=actor.organization_id)
    if not actor.sees_all_clients:
        queryset = queryset.filter(client_id__in=actor.client_ids)
    if actor.sees_only_assigned:
        queryset = queryset.filter(owner_id=actor.user_id)
    return queryset
