# Generated by Django 4.1.8 on 2023-10-25 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0011_alter_eventprogramcategory_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventtag',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Neaktivní štítky se nezobrazí organizátorovi při vytváření nové akce'),
        ),
    ]