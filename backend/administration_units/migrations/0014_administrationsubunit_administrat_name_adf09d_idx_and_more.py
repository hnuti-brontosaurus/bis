# Generated by Django 4.1.8 on 2024-05-13 10:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("administration_units", "0013_administrationunit__search_field"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="administrationsubunit",
            index=models.Index(fields=["name"], name="administrat_name_adf09d_idx"),
        ),
        migrations.AddIndex(
            model_name="administrationunit",
            index=models.Index(
                fields=["abbreviation"], name="administrat_abbrevi_e5b92f_idx"
            ),
        ),
    ]