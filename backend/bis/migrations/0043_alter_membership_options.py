# Generated by Django 4.1.8 on 2024-01-21 23:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0042_auto_20240118_1008"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="membership",
            options={"ordering": ("-year", "user__last_name", "user__first_name")},
        ),
    ]