# Generated by Django 4.1.8 on 2024-01-18 14:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("other", "0008_donationpoints_file"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Feedback",
        ),
    ]