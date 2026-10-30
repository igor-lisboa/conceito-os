from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, ListView

from apps.accounts.mixins import CapabilityRequiredMixin
from apps.accounts.models import Membership
from apps.accounts.permissions import Capability
from apps.accounts.roles import Role
from apps.clients.queries import visible_clients

from .models import Task
from .queries import visible_tasks

User = get_user_model()


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "client", "owner", "due_date"]
        labels = {
            "title": _("Task"),
            "client": _("Client"),
            "owner": _("Responsible"),
            "due_date": _("Due date"),
        }
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, membership, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].required = False
        self.fields["client"].queryset = visible_clients(membership)
        self.fields["owner"].required = False
        internal = Membership.objects.filter(organization=membership.organization).exclude(role=Role.CLIENT.value)
        self.fields["owner"].queryset = User.objects.filter(memberships__in=internal).distinct()


class TaskListView(CapabilityRequiredMixin, ListView):
    required_capability = Capability.ACCESS_INTERNAL
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        queryset = visible_tasks(self.request.membership).select_related("client", "owner")
        if self.request.GET.get("mine"):
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mine"] = bool(self.request.GET.get("mine"))
        return context


class TaskCreateView(CapabilityRequiredMixin, CreateView):
    required_capability = Capability.EDIT_CONTENT
    template_name = "tasks/task_form.html"
    form_class = TaskForm
    success_url = reverse_lazy("task_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["membership"] = self.request.membership
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.request.membership.organization
        form.instance.created_by = self.request.user
        messages.success(self.request, gettext("Task added."))
        return super().form_valid(form)


class TaskToggleView(CapabilityRequiredMixin, View):
    required_capability = Capability.ACCESS_INTERNAL
    http_method_names = ["post"]

    def post(self, request, pk):
        task = get_object_or_404(visible_tasks(request.membership), pk=pk)
        task.mark_done(done=not task.is_done)
        return redirect("task_list")
