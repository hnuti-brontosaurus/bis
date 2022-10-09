# Generated by Django 3.2.15 on 2022-10-09 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0002_alter_zipcode_region'),
        ('bis', '0049_event_is_closed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='region',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='regions.region'),
        ),
    ]