from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .emails import send_welcome_email
from .models import User


@receiver(post_save, sender=User)
def send_welcome_on_creation(sender, instance, created, raw=False, **kwargs):
    """Welcome a new user once their row is committed, so the email never points to a
    user that was rolled back."""
    if created and not raw and instance.email:
        transaction.on_commit(lambda: send_welcome_email(instance))
