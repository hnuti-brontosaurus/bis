# Generated by Django 3.2.17 on 2023-02-26 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bis', '0013_alter_user_vokativ'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='sex',
            new_name='pronoun',
        ),
    ]