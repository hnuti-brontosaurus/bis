from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook_categories", "0010_allergen"),
    ]

    operations = [
        migrations.CreateModel(
            name="IngredientCategory",
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
                ("name", models.CharField(max_length=31)),
                ("slug", models.SlugField()),
                ("order", models.PositiveSmallIntegerField()),
            ],
            options={
                "ordering": ("order",),
                "abstract": False,
            },
        ),
    ]
