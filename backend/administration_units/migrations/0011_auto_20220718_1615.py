# Generated by Django 3.2.14 on 2022-07-18 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration_units', '0010_auto_20220718_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrationunit',
            name='_history',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='brontosaurusmovement',
            name='_history',
            field=models.JSONField(default=dict),
        ),
    ]