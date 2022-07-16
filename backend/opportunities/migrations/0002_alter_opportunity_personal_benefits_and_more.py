# Generated by Django 4.0.5 on 2022-06-16 12:53

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunities', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='personal_benefits',
            field=tinymce.models.HTMLField(help_text='Uveď konkrétní osobní přínos do života z realizace této příležitosti'),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='requirements',
            field=tinymce.models.HTMLField(help_text='Napiš dovednosti, zkušenosti či vybavení potřebné k zapojení do příležitosti'),
        ),
    ]