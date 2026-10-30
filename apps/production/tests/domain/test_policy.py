from dataclasses import dataclass, field
from unittest import TestCase

from apps.production.domain.policy import can_access, can_see_client


@dataclass
class FakeActor:
    user_id: int = 1
    organization_id: int = 1
    sees_all_clients: bool = False
    sees_only_assigned: bool = False
    client_ids: frozenset = field(default_factory=frozenset)


@dataclass
class FakeContent:
    organization_id: int = 1
    client_id: int = 5
    owner_id: int | None = 1


class PolicyTests(TestCase):
    def test_owner_can_access_any_client_of_their_organization(self):
        owner = FakeActor(sees_all_clients=True)
        self.assertTrue(can_access(owner, FakeContent(client_id=99)))

    def test_nobody_crosses_organizations(self):
        owner_of_other_agency = FakeActor(organization_id=2, sees_all_clients=True)
        self.assertFalse(can_access(owner_of_other_agency, FakeContent(organization_id=1)))

    def test_manager_needs_the_client_to_be_assigned(self):
        manager = FakeActor(client_ids=frozenset({5}))
        self.assertTrue(can_access(manager, FakeContent(client_id=5)))
        self.assertFalse(can_access(manager, FakeContent(client_id=6)))

    def test_freelancer_only_sees_pieces_assigned_to_them(self):
        freelancer = FakeActor(user_id=8, client_ids=frozenset({5}), sees_only_assigned=True)
        self.assertTrue(can_access(freelancer, FakeContent(client_id=5, owner_id=8)))
        self.assertFalse(can_access(freelancer, FakeContent(client_id=5, owner_id=9)))

    def test_can_see_client_matches_access_rules(self):
        self.assertTrue(can_see_client(FakeActor(sees_all_clients=True), 42))
        self.assertTrue(can_see_client(FakeActor(client_ids=frozenset({42})), 42))
        self.assertFalse(can_see_client(FakeActor(), 42))
