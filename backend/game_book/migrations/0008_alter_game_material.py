# Generated by Django 3.2.17 on 2023-02-24 21:29

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game_book", "0007_auto_20230224_2229"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="material",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Co je potřeba k uvedení hry, soubory pro tisk lze přiložit níže",
            ),
        ),
    ]
