# Generated by Django 3.2.14 on 2022-07-18 15:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bis', '0024_user_close_person'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]