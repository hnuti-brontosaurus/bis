# Generated by Django 4.1.8 on 2024-01-17 12:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("other", "0005_donationpointsaggregation_donationpointscolumn_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="donationpoints",
            name="sections",
        ),
        migrations.RemoveField(
            model_name="donationpointssection",
            name="columns",
        ),
        migrations.AddField(
            model_name="donationpointscolumn",
            name="section",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="columns",
                to="other.donationpointssection",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="donationpointssection",
            name="donation_points",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sections",
                to="other.donationpoints",
            ),
            preserve_default=False,
        ),
    ]
