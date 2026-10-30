from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 50

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationOpenView(LoginRequiredMixin, View):
    """Mark one notification as read and go to the item it talks about."""

    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at"])
        return redirect(notification.url)


class NotificationReadAllView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request):
        Notification.objects.filter(recipient=request.user, read_at__isnull=True).update(read_at=timezone.now())
        return redirect("notification_list")
