"""Comments on a piece, and the people they mention (TD-29, PRO-004, NTF-006).

A mention is an email address written after @ in the comment, for example
"@ana@agencia.com.br". Only people who already belong to the organization are
notified; an address that is not a member is ignored.
"""

import re

from django.utils import timezone

from apps.notifications.adapters import DjangoNotifier

from .models import Comment

MENTION = re.compile(r"@([\w.+-]+@[\w-]+(?:\.[\w-]+)+)")


def mentioned_emails(body):
    return {match.lower() for match in MENTION.findall(body or "")}


def add_comment(content, author, body):
    """Save the comment and notify every mentioned member of the organization."""
    from apps.accounts.models import Membership

    comment = Comment.objects.create(
        organization=content.organization,
        content=content,
        author=author,
        body=body.strip(),
    )
    emails = mentioned_emails(body)
    if emails:
        members = Membership.objects.filter(
            organization=content.organization,
            user__email__in=emails,
        ).exclude(user=author).select_related("user")
        DjangoNotifier().notify_users(
            users=[membership.user for membership in members],
            kind="mention",
            organization_id=content.organization_id,
            content_id=content.pk,
            title=content.title,
            actor_user_id=author.pk,
            event_key=f"mention:{comment.pk}",
            extra={"author": author.get_full_name() or author.email},
        )
    return comment


def can_change_comment(comment, user):
    """Only the author changes a comment (TD-S13, PROPOSAL pending the product owner)."""
    return comment.author_id is not None and comment.author_id == user.pk


def update_comment(comment, body):
    """Replace the text and mark the comment as edited. Mentions are not notified again (PROPOSAL)."""
    comment.body = body.strip()
    comment.edited_at = timezone.now()
    comment.save(update_fields=["body", "edited_at"])
    return comment


def delete_comment(comment):
    """Remove the comment from the piece. Notifications already sent stay where they were sent."""
    comment.delete()
