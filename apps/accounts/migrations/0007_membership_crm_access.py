# Adds the per-person CRM permission (D-16, answer 4B).
#
# Account managers already had CRM access before this change. They keep it: the data step
# grants it to every existing account manager. Owners can stop it per person afterwards.

from django.db import migrations, models


def grant_crm_to_existing_account_managers(apps, schema_editor):
    Membership = apps.get_model("accounts", "Membership")
    Membership.objects.filter(role="account_manager").update(crm_access=True)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_soft_delete"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="crm_access",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(grant_crm_to_existing_account_managers, migrations.RunPython.noop),
    ]
