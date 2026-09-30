from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0034_recipe_difficulty_note"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="servings_note",
            field=models.TextField(blank=True),
        ),
    ]
