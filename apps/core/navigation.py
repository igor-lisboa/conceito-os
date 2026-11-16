"""Shared desktop/mobile navigation, using the same capabilities as the views."""

from django.urls import reverse
from django.utils.translation import gettext as _

from apps.accounts.permissions import Capability, has_capability
from apps.accounts.roles import Role


def navigation(request):
    membership = getattr(request, "membership", None)
    if membership is None:
        return {}

    def item(route, label, icon, prefix=None):
        url = reverse(route)
        return {"url": url, "label": label, "icon": icon,
                "active": request.path.startswith(prefix or url)}

    if membership.role == Role.CLIENT:
        work = [item("portal_list", _("Approvals"), "check", "/portal/"),
                item("portal_calendar", _("Calendar"), "calendar"),
                item("portal_results", _("Results"), "chart"),
                item("portal_files", _("Files"), "folder"),
                item("portal_contact", _("Contact"), "mail")]
        # Portal detail/approval pages share the list entry; other sections are separate.
        work[0]["active"] = request.path == work[0]["url"] or (
            request.path.startswith("/portal/") and not any(i["active"] for i in work[1:]))
        groups = [{"label": _("Client space"), "items": work}]
        mobile = [work[0], work[1], work[3], work[4]]
    else:
        work = [item("home", _("Home"), "home"),
                item("client_list", _("Clients"), "users"),
                item("content_list", _("Content"), "layers")]
        work[-1]["active"] = work[-1]["active"] and not request.path.startswith(
            (reverse("content_calendar"), reverse("content_board")))
        planning = [item("content_calendar", _("Calendar"), "calendar"),
                    item("content_board", _("Board"), "board"),
                    item("task_list", _("Tasks"), "check"),
                    item("report", _("Reports"), "chart")]
        if has_capability(membership, Capability.MANAGE_CRM):
            work.append(item("lead_board", _("Sales"), "trend", "/crm/"))
        groups = [{"label": _("Workspace"), "items": work},
                  {"label": _("Planning"), "items": planning}]
        if has_capability(membership, Capability.MANAGE_TEAM):
            groups.append({"label": _("Administration"), "items": [
                item("team_list", _("Team"), "users", "/accounts/team/"),
                item("organization_settings", _("Settings"), "settings"),
                item("audit_log", _("Audit log"), "shield"),
            ]})
        mobile = [work[0], work[1], planning[0], planning[2]]

    utility_labels = {
        "account": _("Account"), "mfa_setup": _("Security"),
        "mfa_verify": _("Security"), "notification_list": _("Notifications"),
    }
    route_name = request.resolver_match.url_name if request.resolver_match else ""
    current = next((i["label"] for g in groups for i in g["items"] if i["active"]),
                   utility_labels.get(route_name, _("Workspace")))
    return {"navigation_groups": groups, "mobile_navigation": mobile, "current_section": current}
