# Generated by Django 4.1.8 on 2023-10-23 11:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0018_event_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="created_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
