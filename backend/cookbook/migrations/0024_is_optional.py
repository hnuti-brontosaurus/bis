from django.db import migrations, models


def flip_required_to_optional(apps, schema_editor):
    RecipeIngredient = apps.get_model("cookbook", "RecipeIngredient")
    for row in RecipeIngredient.objects.all():
        row.is_optional = not row.is_required
        row.save(update_fields=["is_optional"])


def flip_optional_to_required(apps, schema_editor):
    RecipeIngredient = apps.get_model("cookbook", "RecipeIngredient")
    for row in RecipeIngredient.objects.all():
        row.is_required = not row.is_optional
        row.save(update_fields=["is_required"])


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0023_cart"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipeingredient",
            name="is_optional",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="recipestep",
            name="is_optional",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(flip_required_to_optional, flip_optional_to_required),
        migrations.RemoveField(
            model_name="recipeingredient",
            name="is_required",
        ),
    ]
