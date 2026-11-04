"""Record how each publication happened (INT-010).

Every piece published so far was marked by hand, so existing published pieces are backfilled as "manual".
"""

from django.db import migrations, models


def _backfill_manual(apps, schema_editor):
    ContentItem = apps.get_model("production", "ContentItem")
    ContentItem.objects.filter(state="published").update(publish_method="manual")


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0003_comment_edited_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentitem',
            name='publish_method',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.RunPython(_backfill_manual, migrations.RunPython.noop),
    ]
