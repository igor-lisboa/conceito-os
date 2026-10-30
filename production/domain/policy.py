"""Who may see a piece of content. Pure rules, no database.

The read side (production/queries.py) applies the same rules as a database
filter. Tests check both sides agree.
"""


def can_see_client(actor, client_id):
    return actor.sees_all_clients or client_id in actor.client_ids


def can_access(actor, content):
    if actor.organization_id != content.organization_id:
        return False
    if not can_see_client(actor, content.client_id):
        return False
    if actor.sees_only_assigned and content.owner_id != actor.user_id:
        return False
    return True
