"""The read side (database filter) must agree with the domain policy.

If these ever disagree, a list could show a piece that the service would refuse
to open, or hide one the user is allowed to see. This test checks both sides
on the same data.
"""

from django.test import TestCase

from accounts.roles import Role
from clients.models import Client, ClientAccess
from core.actors import actor_for
from core.testing import make_membership, make_organization, make_owner
from production.composition import build_content_service
from production.domain.content import Channel, ContentFormat, VersionData
from production.domain.policy import can_access
from production.models import ContentItem
from production.queries import visible_content


class ReadSideMatchesPolicyTests(TestCase):
    def setUp(self):
        self.agency = make_organization("Agência A")
        self.other_agency = make_organization("Agência B")
        self.owner = make_owner(self.agency)
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        self.freelancer = make_membership(self.agency, Role.FREELANCER)
        self.creative_in_other = make_membership(self.other_agency, Role.CREATIVE)

        self.assigned = Client.objects.create(organization=self.agency, name="Assinado")
        self.unassigned = Client.objects.create(organization=self.agency, name="Não assinado")
        ClientAccess.objects.create(organization=self.agency, client=self.assigned, membership=self.manager)
        ClientAccess.objects.create(organization=self.agency, client=self.assigned, membership=self.freelancer)

        service = build_content_service()
        self.pieces = []
        for client, owner in [
            (self.assigned, None),
            (self.assigned, self.freelancer.user),
            (self.unassigned, None),
        ]:
            content_id = service.create(
                actor_for(self.owner),
                client_id=client.pk,
                title=f"{client.name} / {owner}",
                channel=Channel.TIKTOK.value,
                content_format=ContentFormat.TIKTOK_VIDEO.value,
                owner_id=owner.pk if owner else None,
                version=VersionData(caption="x"),
            )
            self.pieces.append(ContentItem.objects.get(pk=content_id))

    def assert_list_matches_policy(self, membership):
        actor = actor_for(membership)
        listed = set(visible_content(actor).values_list("pk", flat=True))
        allowed = {piece.pk for piece in self.pieces if can_access(actor, self._as_domain(piece))}
        self.assertEqual(listed, allowed)
        return listed

    def _as_domain(self, row):
        from production.adapters.django_repository import DjangoContentRepository

        return DjangoContentRepository().get(row.organization_id, row.pk)

    def test_owner_sees_every_piece_of_their_agency(self):
        self.assertEqual(len(self.assert_list_matches_policy(self.owner)), 3)

    def test_manager_sees_only_assigned_clients(self):
        self.assertEqual(len(self.assert_list_matches_policy(self.manager)), 2)

    def test_freelancer_sees_only_the_piece_assigned_to_them(self):
        self.assertEqual(len(self.assert_list_matches_policy(self.freelancer)), 1)

    def test_other_agency_sees_nothing(self):
        self.assertEqual(len(self.assert_list_matches_policy(self.creative_in_other)), 0)
