# Generated by Django 3.2.14 on 2022-07-16 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bis', '0019_auto_20220716_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='web',
            field=models.URLField(blank=True),
        ),
    ]