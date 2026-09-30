from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0033_recipe_default_servings_recipe_servings_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="difficulty_note",
            field=models.TextField(blank=True),
        ),
    ]
