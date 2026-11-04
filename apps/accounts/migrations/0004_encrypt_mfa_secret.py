"""Encrypt the MFA secrets already stored in plain text (TD-S11).

Steps: widen the column, encrypt each existing plain secret in place, then switch
the field to the encrypted field class. The reverse path decrypts back to plain text.

The data step uses raw SQL so it never goes through the field's own conversion:
it reads and writes exactly what is stored.
"""

from django.db import connection, migrations, models

import apps.accounts.fields


def _rewrite_secrets(apps, schema_editor, transform):
    device_model = apps.get_model("accounts", "MFADevice")
    db = schema_editor.connection if schema_editor is not None else connection
    table = db.ops.quote_name(device_model._meta.db_table)
    pk = db.ops.quote_name(device_model._meta.pk.column)
    column = db.ops.quote_name("secret")
    with db.cursor() as cursor:
        cursor.execute(f"SELECT {pk}, {column} FROM {table}")
        rows = cursor.fetchall()
        for row_pk, stored in rows:
            if not stored:
                continue
            new_value = transform(stored)
            if new_value != stored:
                cursor.execute(f"UPDATE {table} SET {column} = %s WHERE {pk} = %s", [new_value, row_pk])


def _encrypt_existing(apps, schema_editor):
    from apps.accounts.fields import encrypt_secret, is_encrypted

    _rewrite_secrets(apps, schema_editor, lambda stored: stored if is_encrypted(stored) else encrypt_secret(stored))


def _decrypt_existing(apps, schema_editor):
    from apps.accounts.fields import decrypt_secret, is_encrypted

    _rewrite_secrets(apps, schema_editor, lambda stored: decrypt_secret(stored) if is_encrypted(stored) else stored)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_email_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mfadevice',
            name='secret',
            field=models.CharField(max_length=255),
        ),
        migrations.RunPython(_encrypt_existing, _decrypt_existing),
        migrations.AlterField(
            model_name='mfadevice',
            name='secret',
            field=apps.accounts.fields.EncryptedSecretField(max_length=255),
        ),
    ]
