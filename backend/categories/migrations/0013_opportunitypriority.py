# Generated by Django 4.1.8 on 2024-01-18 10:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0012_alter_eventtag_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="OpportunityPriority",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=63)),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
    ]