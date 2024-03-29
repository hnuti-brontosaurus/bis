# Generated by Django 4.1.8 on 2023-10-25 11:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0026_rename_is_fully_specified_location_is_traditional_and_more"),
        ("event", "0011_alter_vipeventpropagation_goals_of_event_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventfinance",
            name="event",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="finance",
                to="bis.event",
            ),
        ),
        migrations.AlterField(
            model_name="eventrecord",
            name="event",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="record",
                to="bis.event",
            ),
        ),
    ]
