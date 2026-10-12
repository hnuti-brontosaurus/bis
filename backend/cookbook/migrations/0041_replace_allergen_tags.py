from django.db import migrations


def refresh_allergens(apps, schema_editor):
    Allergen = apps.get_model("cookbook_categories", "Allergen")
    Recipe = apps.get_model("cookbook", "Recipe")
    for recipe in Recipe.objects.all():
        recipe.allergens.set(
            Allergen.objects.filter(
                ingredients__recipe_ingredients__recipe=recipe,
                ingredients__recipe_ingredients__is_optional=False,
            ).distinct()
        )


def replace_allergen_tags(apps, schema_editor):
    # "bez lepku" and "bez sóji" are superseded by the allergen exclude filter.
    # The gluten tag lives on as "bezlepková varianta", which only means
    # something on a recipe that does contain gluten.
    RecipeTag = apps.get_model("cookbook_categories", "RecipeTag")
    RecipeTag.objects.filter(slug="no_soya").delete()
    gluten_free = RecipeTag.objects.filter(slug="gluten_free").first()
    if gluten_free is None:
        return
    gluten_free.slug = "gluten_free_variant"
    gluten_free.name = "bezlepková varianta"
    gluten_free.save()
    gluten_free.recipes.remove(*gluten_free.recipes.exclude(allergens__slug="gluten"))


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0040_article_images"),
        ("cookbook_categories", "0011_ingredientcategory"),
    ]

    operations = [
        migrations.RunPython(refresh_allergens, migrations.RunPython.noop),
        migrations.RunPython(replace_allergen_tags, migrations.RunPython.noop),
    ]
