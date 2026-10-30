"""Django adapter for the ContentRepository port.

Translates between the Content aggregate (domain) and the ContentItem /
ContentVersion / Approval tables (persistence).

Versions and approvals are append-only in the domain, so saving only inserts
the rows that are new. That keeps the adapter small and easy to reason about.
"""

from apps.accounts.models import Membership
from apps.accounts.roles import Role
from apps.clients.models import Client

from ..domain.content import (
    Approval,
    ApprovalDecision,
    ApprovalStage,
    Channel,
    Content,
    ContentFormat,
    Version,
    VersionData,
)
from ..domain.states import ContentState
from ..models import Approval as ApprovalRow
from ..models import ContentItem, ContentVersion


class DjangoContentRepository:
    def get(self, organization_id, content_id):
        row = (
            ContentItem.objects.filter(organization_id=organization_id, pk=content_id)
            .prefetch_related("versions", "approvals__version")
            .first()
        )
        return _to_domain(row) if row else None

    def save(self, content):
        if content.id is None:
            row = ContentItem(organization_id=content.organization_id)
        else:
            row = ContentItem.objects.get(pk=content.id)

        row.client_id = content.client_id
        row.owner_id = content.owner_id
        row.title = content.title
        row.channel = content.channel.value
        row.content_format = content.content_format.value
        row.state = content.state.value
        row.client_approval_required = content.client_approval_required
        row.scheduled_for = content.scheduled_for
        row.published_at = content.published_at
        row.published_url = content.published_url
        row.failure_reason = content.failure_reason
        row.save()
        content.id = row.id

        self._insert_new_versions(row, content)
        self._insert_new_approvals(row, content)

    def client_approval_rule(self, organization_id, client_id):
        # Archived clients are treated as missing: no new content for them.
        return (
            Client.objects.filter(organization_id=organization_id, pk=client_id, archived_at__isnull=True)
            .values_list("client_approval_required", flat=True)
            .first()
        )

    def is_internal_member(self, organization_id, user_id):
        return (
            Membership.objects.filter(organization_id=organization_id, user_id=user_id)
            .exclude(role=Role.CLIENT.value)
            .exists()
        )

    def _insert_new_versions(self, row, content):
        already_saved = row.versions.count()
        for version in content.versions[already_saved:]:
            ContentVersion.objects.create(
                organization_id=content.organization_id,
                content=row,
                number=version.number,
                caption=version.data.caption,
                cta=version.data.cta,
                script=version.data.script,
                media_url=version.data.media_url,
                created_by_id=version.created_by_user_id,
            )

    def _insert_new_approvals(self, row, content):
        already_saved = row.approvals.count()
        for approval in content.approvals[already_saved:]:
            ApprovalRow.objects.create(
                organization_id=content.organization_id,
                content=row,
                version=row.versions.get(number=approval.version_number),
                stage=approval.stage.value,
                decision=approval.decision.value,
                comment=approval.comment,
                actor_id=approval.actor_user_id,
            )


def _to_domain(row):
    return Content(
        id=row.id,
        organization_id=row.organization_id,
        client_id=row.client_id,
        owner_id=row.owner_id,
        title=row.title,
        channel=Channel(row.channel),
        content_format=ContentFormat(row.content_format),
        client_approval_required=row.client_approval_required,
        state=ContentState(row.state),
        versions=[
            Version(
                number=version.number,
                data=VersionData(
                    caption=version.caption,
                    cta=version.cta,
                    script=version.script,
                    media_url=version.media_url,
                ),
                created_by_user_id=version.created_by_id,
            )
            for version in row.versions.all()
        ],
        approvals=[
            Approval(
                version_number=approval.version.number,
                stage=ApprovalStage(approval.stage),
                decision=ApprovalDecision(approval.decision),
                comment=approval.comment,
                actor_user_id=approval.actor_id,
            )
            for approval in row.approvals.all()
        ],
        scheduled_for=row.scheduled_for,
        published_at=row.published_at,
        published_url=row.published_url,
        failure_reason=row.failure_reason,
    )
