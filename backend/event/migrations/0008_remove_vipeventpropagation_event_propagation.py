# Generated by Django 4.0.10 on 2023-03-05 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0007_auto_20230305_1959'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vipeventpropagation',
            name='event_propagation',
        ),
    ]