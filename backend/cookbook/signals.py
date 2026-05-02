"""Cheap, synchronous Ingredient normalization.

Anything that talks to the network (Groq enrichment) lives in
`cookbook.services.ingredient_enrichment` and is invoked by the API view —
not from a `pre_save` signal. Signals run inside the request thread on every
save (admin, shell, fixtures, ...) and a network call there blocks the
request and hides errors.
"""

from cookbook.models.ingredients import Ingredient
from cookbook.models.recipes import Recipe, RecipeIngredient
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Ingredient, dispatch_uid="ingredient_normalize_name")
def ingredient_normalize_name(instance: Ingredient, **kwargs):
    instance.name = " ".join(instance.name.split())
    if instance.pk is None and instance.name:
        instance.name = instance.name.lower().capitalize()


# --- Recipe.allergens cache ----------------------------------------------
# Recipe.allergens is denormalized so read paths (list filter / detail page)
# can use it directly without recomputing the union from ingredients. These
# signals refresh the cache whenever something that contributes to it
# changes. M2M.set() short-circuits at the SQL level when nothing actually
# changed, so signal cascades are cheap.


@receiver(post_save, sender=RecipeIngredient, dispatch_uid="recipe_ingredient_save")
@receiver(post_delete, sender=RecipeIngredient, dispatch_uid="recipe_ingredient_delete")
def _refresh_on_recipe_ingredient_change(instance: RecipeIngredient, **kwargs):
    instance.recipe.refresh_allergens()


@receiver(
    m2m_changed,
    sender=Ingredient.allergens.through,
    dispatch_uid="ingredient_allergens_changed",
)
def _refresh_on_ingredient_allergens_change(instance: Ingredient, action, **kwargs):
    # post_add / post_remove / post_clear cover all mutations of the M2M.
    if not action.startswith("post_"):
        return
    for recipe in Recipe.objects.filter(ingredients__ingredient=instance).distinct():
        recipe.refresh_allergens()
