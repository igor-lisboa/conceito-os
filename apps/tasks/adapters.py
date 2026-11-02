"""Django adapter for the task dates port used when a planned date changes (CAL-003).

A task follows the piece only when it was due on the old planned day, is still open,
and is linked to that piece. A task with its own deadline is left alone.
"""

from django.utils import timezone

from .models import Task


class DjangoTaskDates:
    def follow_planned_date(self, organization_id, content_id, *, previous, current):
        old_day = timezone.localdate(previous)
        new_day = timezone.localdate(current)
        if old_day == new_day:
            return 0
        return Task.objects.filter(
            organization_id=organization_id,
            content_id=content_id,
            done_at__isnull=True,
            due_date=old_day,
        ).update(due_date=new_day)
