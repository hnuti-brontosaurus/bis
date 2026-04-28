from django.db import models as m
from django.db.models import PROTECT

from bis.models import User
from cookbook.models.base import BaseModel, ChangeMixin
from cookbook.models.ingredients import Ingredient
from cookbook.models.recipes import Recipe
from cookbook_categories.models import Unit
from translation.translate import translate_model


@translate_model
class Menu(ChangeMixin, BaseModel):
    name = m.CharField(max_length=31)
    description = m.TextField(blank=True)
    user = m.ForeignKey(User, related_name="menus", on_delete=PROTECT)
    is_shared = m.BooleanField(default=False)
    is_starred = m.BooleanField(default=False)


@translate_model
class MenuRecipe(BaseModel):
    menu = m.ForeignKey(Menu, related_name="menu_recipes", on_delete=PROTECT)
    name = m.CharField(max_length=31)
    original = m.ForeignKey(
        Recipe, related_name="menu_recipes", on_delete=PROTECT, blank=True, null=True
    )
    note = m.TextField(blank=True)
    served_at = m.DateTimeField(blank=True, null=True)


@translate_model
class MenuRecipeIngredient(BaseModel):
    menu_recipe = m.ForeignKey(
        MenuRecipe, related_name="menu_recipe_ingredients", on_delete=PROTECT
    )
    ingredient = m.ForeignKey(
        Ingredient, related_name="menu_recipe_ingredients", on_delete=PROTECT
    )
    unit = m.ForeignKey(Unit, related_name="menu_recipe_ingredients", on_delete=PROTECT)
    amount = m.FloatField()
    is_used = m.BooleanField()
    comment = m.TextField(blank=True)
