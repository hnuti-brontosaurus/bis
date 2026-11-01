from django.db import migrations


def tag_desserts(apps, schema_editor):
    # Deploys migrate before create_categories, so the tag may not exist yet;
    # create_categories then fixes its order.
    RecipeTag = apps.get_model("cookbook_categories", "RecipeTag")
    Recipe = apps.get_model("cookbook", "Recipe")
    desserts = Recipe.objects.filter(tags__slug__in=["cake", "bun", "candy"]).distinct()
    if not desserts.exists():
        return
    dessert, _ = RecipeTag.objects.get_or_create(
        slug="dessert", defaults=dict(name="dezert", group="Chody", order=0)
    )
    dessert.recipes.add(*desserts)


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0041_replace_allergen_tags"),
        ("cookbook_categories", "0011_ingredientcategory"),
    ]

    operations = [
        migrations.RunPython(tag_desserts, migrations.RunPython.noop),
    ]
