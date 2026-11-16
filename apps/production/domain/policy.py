"""Who may see a piece of content. Pure rules, no database.

The rule is written once, in `Scope`: `allows` decides one piece in Python, and
`filter_queryset` expresses the same rule as a database filter for lists and counts.
Both live side by side here, so a change to the rule is made in one place (TD-S4).
tests/test_queries.py checks that the two agree.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Scope:
    organization_id: int
    user_id: int
    sees_all_clients: bool
    sees_only_assigned: bool
    client_ids: frozenset

    @classmethod
    def of(cls, actor):
        return cls(
            organization_id=actor.organization_id,
            user_id=actor.user_id,
            sees_all_clients=actor.sees_all_clients,
            sees_only_assigned=actor.sees_only_assigned,
            client_ids=frozenset(actor.client_ids),
        )

    def allows(self, organization_id, client_id, owner_id):
        """The rule for one piece: same organization, a visible client, and (for freelancers) their own."""
        if organization_id != self.organization_id:
            return False
        if not self.sees_all_clients and client_id not in self.client_ids:
            return False
        if self.sees_only_assigned and owner_id != self.user_id:
            return False
        return True

    def filter_queryset(self, queryset):
        """The same rule as `allows`, applied to a queryset of content."""
        queryset = queryset.filter(organization_id=self.organization_id)
        if not self.sees_all_clients:
            queryset = queryset.filter(client_id__in=self.client_ids)
        if self.sees_only_assigned:
            queryset = queryset.filter(owner_id=self.user_id)
        return queryset


def can_see_client(actor, client_id):
    return actor.sees_all_clients or client_id in actor.client_ids


def can_access(actor, content):
    return Scope.of(actor).allows(content.organization_id, content.client_id, content.owner_id)
