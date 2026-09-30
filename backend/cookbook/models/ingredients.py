from cookbook.models.base import BaseModel, ChangeMixin
from cookbook_categories.models import Allergen, IngredientCategory
from django.db import models as m
from translation.translate import translate_model


def other_category_id():
    return IngredientCategory.objects.get(slug="other").id


@translate_model
class Ingredient(ChangeMixin, BaseModel):
    name = m.CharField(max_length=31, unique=True)
    state = m.CharField(
        max_length=13,
        choices=[("solid", "Pevné"), ("liquid", "Tekuté")],
        default="solid",
    )
    g_per_piece = m.PositiveSmallIntegerField(blank=True, null=True)
    g_per_liter = m.PositiveSmallIntegerField(blank=True, null=True)
    g_per_serving = m.PositiveSmallIntegerField(blank=True, null=True)
    category = m.ForeignKey(
        IngredientCategory,
        related_name="ingredients",
        on_delete=m.PROTECT,
        default=other_category_id,
    )
    reasoning = m.TextField(blank=True)
    allergens = m.ManyToManyField(Allergen, related_name="ingredients", blank=True)
