# Generated by Django 4.1.8 on 2023-10-23 11:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0008_alter_eventtag_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventprogramcategory",
            name="notification_email",
            field=models.EmailField(default="hnuti@brontosaurus.cz", max_length=254),
        ),
    ]
