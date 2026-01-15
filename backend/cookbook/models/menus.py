from cookbook.models.base import BaseModel, ChangeMixin
from cookbook.models.ingredients import Ingredient
from cookbook.models.recipes import Recipe
from cookbook_categories.models import Unit
from django.db.models import *
from translation.translate import translate_model

from bis.models import User


@translate_model
class Menu(ChangeMixin, BaseModel):
    name = CharField(max_length=31)
    description = TextField(blank=True)
    user = ForeignKey(User, related_name="menus", on_delete=PROTECT)
    is_shared = BooleanField(default=False)
    is_starred = BooleanField(default=False)


@translate_model
class MenuRecipe(BaseModel):
    menu = ForeignKey(Menu, related_name="menu_recipes", on_delete=PROTECT)
    name = CharField(max_length=31)
    original = ForeignKey(
        Recipe, related_name="menu_recipes", on_delete=PROTECT, blank=True, null=True
    )
    note = TextField(blank=True)
    served_at = DateTimeField(blank=True, null=True)


@translate_model
class MenuRecipeIngredient(BaseModel):
    menu_recipe = ForeignKey(
        MenuRecipe, related_name="menu_recipe_ingredients", on_delete=PROTECT
    )
    ingredient = ForeignKey(
        Ingredient, related_name="menu_recipe_ingredients", on_delete=PROTECT
    )
    unit = ForeignKey(Unit, related_name="menu_recipe_ingredients", on_delete=PROTECT)
    amount = DecimalField(max_digits=10, decimal_places=1)
    is_used = BooleanField()
    comment = TextField(blank=True)
