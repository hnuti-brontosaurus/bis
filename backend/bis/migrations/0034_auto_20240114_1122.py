# Generated by Django 4.1.8 on 2024-01-14 10:22
from datetime import date

from django.db import migrations


def migrate(apps, schema_editor):
    Membership = apps.get_model("bis", "Membership")
    memberships = []
    for membership in Membership.objects.all():
        membership.created_at = date(membership.year, 1, 1)
        memberships.append(membership)

    Membership.objects.bulk_update(memberships, ["created_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0033_membership_created_at"),
    ]

    operations = [migrations.RunPython(migrate, migrations.RunPython.noop)]