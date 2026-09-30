from django.db import migrations

CATEGORIES = {
    "fruit_vegetables": (
        "Ovoce a zelenina",
        [
            "Banán",
            "Brambory",
            "Cibule",
            "Česnek",
            "Květák",
            "Ovoce",
            "Citrónová kůra",
        ],
    ),
    "bakery": ("Pečivo", []),
    "chilled": (
        "Nemléčné a chlazené",
        [
            "Mléko",
            "Ovesné mléko",
            "Rostlinné mléko",
            "Sójové mléko",
            "Smetana",
            "Smetana ke šlehání",
            "Silken tofu",
            "Margarín",
            "Alsan",
            "Droždí",
        ],
    ),
    "pantry": ("Trvanlivé", ["Hrách", "Jablečné pyré"]),
    "baking": (
        "Pečení",
        [
            "Hladká mouka",
            "Polohrubá mouka",
            "Polohrubá mouka celozrnná",
            "Hrubá mouka",
            "Cukr krystal",
            "Cukr krupice",
            "Cukr moučka",
            "Kokosový cukr",
            "Vanilkový cukr",
            "Kukuřičný škrob",
            "Prášek do pečiva",
            "Prášek do perníku",
            "Jedlá soda",
            "Vanilka",
            "Vanilkový extrakt",
            "Kakao",
        ],
    ),
    "sweets": (
        "Sladké",
        [
            "Čokoláda",
            "Hořká čokoláda",
            "Čekankový sirup",
            "Rybízová marmeláda",
            "Kandované ovoce",
        ],
    ),
    "nuts_seeds": (
        "Ořechy a semínka",
        [
            "Mandle",
            "Lískové ořechy",
            "Vlašské ořechy",
            "Kokos",
            "Lněná semínka",
            "Lněné semínko",
            "Datle",
            "Rozinky",
        ],
    ),
    "spices": (
        "Koření",
        [
            "Sůl",
            "Černá sůl",
            "Pepř",
            "Skořice",
            "Muškátový oříšek",
            "Lahůdkové droždí",
        ],
    ),
    "oils_sauces": (
        "Oleje a omáčky",
        [
            "Olej",
            "Řepkový olej",
            "Dezodorizovaný kokosový olej",
            "Jablečný ocet",
            "Ume ocet",
        ],
    ),
    "drinks": ("Nápoje", ["Espresso", "Voda"]),
    "frozen": ("Mražené", []),
    "other": ("Ostatní", ["Proteinový prášek"]),
}


def categorize(apps, schema_editor):
    # Deploys run create_categories only after migrate, so the categories
    # have to exist before the ingredients can point at them.
    IngredientCategory = apps.get_model("cookbook_categories", "IngredientCategory")
    Ingredient = apps.get_model("cookbook", "Ingredient")
    for order, (slug, (name, ingredient_names)) in enumerate(CATEGORIES.items()):
        category, _ = IngredientCategory.objects.update_or_create(
            slug=slug, defaults=dict(name=name, order=order)
        )
        Ingredient.objects.filter(name__in=ingredient_names).update(category=category)


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0028_ingredient_category"),
    ]

    operations = [migrations.RunPython(categorize, migrations.RunPython.noop)]
