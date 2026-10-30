"""Team: invite people, give them clients, and remove their access (TD-03)."""

import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import Membership, User
from accounts.roles import Role
from clients.models import Client, ClientAccess
from core.models import AuditEvent
from core.testing import make_membership, make_organization, make_owner


class InviteTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.clinic = Client.objects.create(organization=self.agency, name="Clínica")
        self.client.force_login(self.owner.user)

    def invite(self, email, role, clients=()):
        return self.client.post(
            reverse("team_invite"),
            {"email": email, "role": role, "clients": [c.pk for c in clients]},
        )

    def test_owner_invites_a_new_person_with_access_to_chosen_clients_only(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.invite("Ana@Conceito.com.br", Role.CREATIVE.value, clients=[self.bakery])

        self.assertRedirects(response, reverse("team_list"))
        user = User.objects.get(email="ana@conceito.com.br")
        membership = Membership.objects.get(user=user, organization=self.agency)
        self.assertEqual(membership.role, Role.CREATIVE.value)
        self.assertEqual(
            list(ClientAccess.objects.filter(membership=membership).values_list("client__name", flat=True)),
            ["Padaria"],
        )

    def test_invited_person_gets_the_invitation_email_not_the_welcome_one(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.invite("bia@conceito.com.br", Role.FREELANCER.value)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("convidado", mail.outbox[0].subject)  # pt-BR invitation, not the welcome text
        self.assertIn("/accounts/password/reset/", mail.outbox[0].body)

    def test_the_invitation_link_lets_the_person_set_their_password(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.invite("carla@conceito.com.br", Role.CREATIVE.value)
        path = re.search(r"(/accounts/password/reset/[^/\s]+/[^/\s]+/)", mail.outbox[0].body).group(1)

        final_url = self.client.get(path, follow=True).redirect_chain[-1][0]
        self.client.post(final_url, {"new_password1": "Senha-Nova-2026!", "new_password2": "Senha-Nova-2026!"})

        self.client.logout()
        self.assertTrue(self.client.login(username="carla@conceito.com.br", password="Senha-Nova-2026!"))

    def test_an_existing_person_is_added_without_a_second_account(self):
        other_agency = make_organization("Outra")
        existing = make_membership(other_agency, Role.CREATIVE, username="dani")
        self.invite(existing.user.email, Role.CREATIVE.value)

        self.assertEqual(User.objects.filter(email=existing.user.email).count(), 1)
        self.assertTrue(Membership.objects.filter(user=existing.user, organization=self.agency).exists())

    def test_inviting_someone_already_in_the_organization_is_refused(self):
        member = make_membership(self.agency, Role.CREATIVE)
        response = self.invite(member.user.email, Role.CREATIVE.value)

        self.assertEqual(Membership.objects.filter(user=member.user, organization=self.agency).count(), 1)
        self.assertEqual(response.status_code, 200)  # the form is shown again with the reason
        self.assertContains(response, "already a member")

    def test_only_owners_can_invite(self):
        creative = make_membership(self.agency, Role.CREATIVE)
        self.client.force_login(creative.user)
        response = self.client.get(reverse("team_invite"))
        self.assertEqual(response.status_code, 403)

    def test_invitations_are_audited(self):
        self.invite("eva@conceito.com.br", Role.CREATIVE.value)
        self.assertTrue(AuditEvent.objects.filter(action="member.invited").exists())


class RemoveAccessTests(TestCase):
    def setUp(self):
        self.agency = make_organization()
        self.owner = make_owner(self.agency)
        self.bakery = Client.objects.create(organization=self.agency, name="Padaria")
        self.manager = make_membership(self.agency, Role.ACCOUNT_MANAGER)
        ClientAccess.objects.create(organization=self.agency, client=self.bakery, membership=self.manager)

    def test_removed_person_loses_access_on_their_next_request(self):
        self.client.force_login(self.manager.user)
        self.assertEqual(self.client.get(reverse("client_detail", args=[self.bakery.pk])).status_code, 200)

        self.client.force_login(self.owner.user)
        self.client.post(reverse("team_remove", args=[self.manager.pk]))

        self.client.force_login(self.manager.user)
        self.assertEqual(self.client.get(reverse("client_detail", args=[self.bakery.pk])).status_code, 403)
        self.assertContains(self.client.get(reverse("home")), "No access yet", status_code=403)
        self.assertFalse(Membership.objects.filter(pk=self.manager.pk).exists())
        self.assertFalse(ClientAccess.objects.filter(membership_id=self.manager.pk).exists())

    def test_removal_keeps_the_person_account(self):
        user_pk = self.manager.user.pk
        self.client.force_login(self.owner.user)
        self.client.post(reverse("team_remove", args=[self.manager.pk]))
        self.assertTrue(User.objects.filter(pk=user_pk).exists())

    def test_owner_cannot_remove_their_own_access(self):
        self.client.force_login(self.owner.user)
        self.client.post(reverse("team_remove", args=[self.owner.pk]))
        self.assertTrue(Membership.objects.filter(pk=self.owner.pk).exists())

    def test_one_of_two_owners_can_be_removed_by_the_other(self):
        second_owner = make_owner(self.agency)
        self.client.force_login(self.owner.user)
        self.client.post(reverse("team_remove", args=[second_owner.pk]))
        self.assertFalse(Membership.objects.filter(pk=second_owner.pk).exists())
        self.assertTrue(Membership.objects.filter(pk=self.owner.pk).exists())

    def test_another_organization_cannot_be_targeted(self):
        outsider_agency = make_organization("Outra")
        outsider = make_membership(outsider_agency, Role.CREATIVE)
        self.client.force_login(self.owner.user)
        response = self.client.post(reverse("team_remove", args=[outsider.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Membership.objects.filter(pk=outsider.pk).exists())

    def test_creatives_cannot_remove_people(self):
        creative = make_membership(self.agency, Role.CREATIVE)
        self.client.force_login(creative.user)
        response = self.client.post(reverse("team_remove", args=[self.manager.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Membership.objects.filter(pk=self.manager.pk).exists())
