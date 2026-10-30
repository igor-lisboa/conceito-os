from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    """Who is acting, in plain terms the application and domain can use.

    The Django edge builds it from a Membership (see core/actors.py). The rest
    of the code never touches the database to find out what the actor may see.
    """

    user_id: int
    organization_id: int
    role: str
    sees_all_clients: bool
    sees_only_assigned: bool
    client_ids: frozenset
