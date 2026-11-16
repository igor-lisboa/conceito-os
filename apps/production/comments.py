"""Comments on a piece, and the people they mention (TD-29, PRO-004, NTF-006, D-31, D-30).

A mention is an email address written after @ in the comment, for example
"@ana@agencia.com.br". Only members who can see the piece are notified (D-31): a mention
never tells someone about a piece they cannot open. An address that is not a member is ignored.
"""

import re

from django.utils import timezone

from apps.accounts.models import Membership
from apps.accounts.permissions import Capability, has_capability
from apps.core.actors import actor_for
from apps.notifications.adapters import DjangoNotifier

from .models import Comment
from .queries import visible_content

MENTION = re.compile(r"@([\w.+-]+@[\w-]+(?:\.[\w-]+)+)")


def mentioned_emails(body):
    return {match.lower() for match in MENTION.findall(body or "")}


def _members_who_can_see(content, emails):
    """Internal members with one of these emails who may open this piece (D-31).

    Internal only: a client-role member may have access to the brand, but internal
    pieces are never shown to them, so a mention must not reach them either.
    """
    candidates = Membership.objects.filter(
        organization_id=content.organization_id,
        user__email__in=emails,
    ).select_related("user")
    return [
        membership
        for membership in candidates
        if has_capability(membership, Capability.ACCESS_INTERNAL)
        and visible_content(actor_for(membership)).filter(pk=content.pk).exists()
    ]


def _notify_mentions(content, author_id, author_name, emails, event_key):
    recipients = [m.user for m in _members_who_can_see(content, emails) if m.user_id != author_id]
    if not recipients:
        return
    DjangoNotifier().notify_users(
        users=recipients,
        kind="mention",
        organization_id=content.organization_id,
        content_id=content.pk,
        title=content.title,
        actor_user_id=author_id,
        event_key=event_key,
        extra={"author": author_name},
    )


def add_comment(content, author, body):
    """Save the comment and notify each mentioned member who can see the piece."""
    comment = Comment.objects.create(
        organization=content.organization,
        content=content,
        author=author,
        body=body.strip(),
    )
    _notify_mentions(
        content,
        author.pk,
        author.get_full_name() or author.email,
        mentioned_emails(body),
        event_key=f"mention:{comment.pk}",
    )
    return comment


def can_change_comment(comment, user):
    """Only the author changes a comment (TD-S13, PROPOSAL pending the product owner)."""
    return comment.author_id is not None and comment.author_id == user.pk


def update_comment(comment, body):
    """Replace the text and mark the comment as edited (PRO-004).

    Decided 2026-11-16 (question 3, option B): a person who is mentioned for the first time
    by an edit is notified. People already mentioned before the edit are not notified again.
    """
    previous = mentioned_emails(comment.body)
    comment.body = body.strip()
    comment.edited_at = timezone.now()
    comment.save(update_fields=["body", "edited_at"])
    new_mentions = mentioned_emails(comment.body) - previous
    if new_mentions:
        author = comment.author
        _notify_mentions(
            comment.content,
            author.pk if author else None,
            (author.get_full_name() or author.email) if author else "",
            new_mentions,
            event_key=f"mention:{comment.pk}:edit:{comment.edited_at.timestamp():.6f}",
        )
    return comment


def delete_comment(comment):
    """Remove the comment from the piece. Notifications already sent stay where they were sent."""
    comment.delete()
