from .models import Notification


def unread_notifications(request):
    """Number of unread notifications for the navigation badge. Empty for anonymous users."""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"unread_notification_count": 0}
    return {
        "unread_notification_count": Notification.objects.filter(
            recipient=user, read_at__isnull=True
        ).count()
    }
