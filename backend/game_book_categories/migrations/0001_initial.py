# Generated by Django 3.2.17 on 2023-02-07 21:37

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GameLengthCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="LocationCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="MaterialRequirementCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="MentalCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OrganizersNumberCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ParticipantAgeCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ParticipantNumberCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PhysicalCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PreparationLengthCategory",
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
                ("name", models.CharField(max_length=15)),
                ("description", models.CharField(max_length=60)),
            ],
            options={
                "ordering": ("id",),
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=15)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
    ]
