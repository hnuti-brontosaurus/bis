# Generated by Django 4.1.8 on 2024-01-17 12:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("other", "0007_alter_donationpointscolumn_points_per_each"),
    ]

    operations = [
        migrations.AddField(
            model_name="donationpoints",
            name="file",
            field=models.FileField(blank=True, upload_to="donation_points"),
        ),
    ]