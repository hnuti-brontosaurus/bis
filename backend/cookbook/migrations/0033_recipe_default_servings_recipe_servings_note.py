import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0032_ingredient_category_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="default_servings",
            field=models.PositiveSmallIntegerField(
                default=2, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="servings_note",
            field=models.CharField(blank=True, max_length=127),
        ),
    ]
