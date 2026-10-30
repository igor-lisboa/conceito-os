"""Leads and proposals, typed in by the team. No research, no automation (PD-02)."""

from django.db import models

from core.choices import translated_choices
from core.enums import LabeledEnum


class LeadStage(LabeledEnum):
    NEW = ("new", "New")
    CONTACTED = ("contacted", "Contacted")
    MEETING = ("meeting", "Meeting")
    WON = ("won", "Won")
    LOST = ("lost", "Lost")


class LeadSource(LabeledEnum):
    REFERRAL = ("referral", "Referral")
    INSTAGRAM = ("instagram", "Instagram")
    WEBSITE = ("website", "Website")
    OTHER = ("other", "Other")


class ProposalStatus(LabeledEnum):
    DRAFT = ("draft", "Draft")
    SENT = ("sent", "Sent")
    ACCEPTED = ("accepted", "Accepted")
    REJECTED = ("rejected", "Rejected")


class Lead(models.Model):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    name = models.CharField(max_length=120)
    source = models.CharField(max_length=20, choices=translated_choices(LeadSource), default=LeadSource.OTHER.value)
    stage = models.CharField(max_length=20, choices=translated_choices(LeadStage), default=LeadStage.NEW.value)
    contact = models.CharField(max_length=160, blank=True)
    next_action = models.CharField(max_length=160, blank=True)
    next_action_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.name


class Proposal(models.Model):
    organization = models.ForeignKey("accounts.Organization", on_delete=models.CASCADE, related_name="+")
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.SET_NULL, related_name="proposals")
    client = models.ForeignKey(
        "clients.Client", null=True, blank=True, on_delete=models.SET_NULL, related_name="proposals"
    )
    title = models.CharField(max_length=160)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=translated_choices(ProposalStatus), default=ProposalStatus.DRAFT.value
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.title
