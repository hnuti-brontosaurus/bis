import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0027_recipeingredient_part"),
        ("cookbook_categories", "0011_ingredientcategory"),
    ]

    operations = [
        migrations.AddField(
            model_name="ingredient",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ingredients",
                to="cookbook_categories.ingredientcategory",
            ),
        ),
    ]
