# Generated by Django 4.1.8 on 2023-10-23 11:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0010_rename_notification_email_eventprogramcategory_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventprogramcategory",
            name="email",
            field=models.EmailField(max_length=254),
        ),
    ]
