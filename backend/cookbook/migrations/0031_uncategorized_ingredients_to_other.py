from django.db import migrations


def set_other(apps, schema_editor):
    IngredientCategory = apps.get_model("cookbook_categories", "IngredientCategory")
    Ingredient = apps.get_model("cookbook", "Ingredient")
    other = IngredientCategory.objects.get(slug="other")
    Ingredient.objects.filter(category=None).update(category=other)


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0030_cart_other_items"),
    ]

    operations = [migrations.RunPython(set_other, migrations.RunPython.noop)]
