# Generated by Django 4.1.8 on 2023-12-06 12:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("administration_units", "0011_administrationsubunit_existed_till"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="administrationsubunit",
            name="existed_till",
        ),
        migrations.AddField(
            model_name="administrationsubunit",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
