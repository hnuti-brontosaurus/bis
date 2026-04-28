from django.db import models as m
from django.db.models import CASCADE, PROTECT

from bis.models import User
from common.thumbnails import ThumbnailImageField
from cookbook.models.base import BaseModel, ChangeMixin
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook_categories.models import (
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from translation.translate import translate_model


@translate_model
class Recipe(ChangeMixin, BaseModel):
    name = m.CharField(max_length=31)
    chef = m.ForeignKey(Chef, related_name="recipes", on_delete=PROTECT)
    difficulty = m.ForeignKey(
        RecipeDifficulty, related_name="recipes", on_delete=PROTECT
    )
    required_time = m.ForeignKey(
        RecipeRequiredTime, related_name="recipes", on_delete=PROTECT
    )
    tags = m.ManyToManyField(RecipeTag, related_name="recipes", blank=True)
    photo = ThumbnailImageField(upload_to="recipes")
    intro = m.TextField()
    sources = m.TextField()
    is_public = m.BooleanField(default=False)


@translate_model
class RecipeIngredient(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="ingredients", on_delete=CASCADE)
    order = m.PositiveSmallIntegerField()
    ingredient = m.ForeignKey(
        Ingredient, related_name="recipe_ingredients", on_delete=PROTECT
    )
    unit = m.ForeignKey(Unit, related_name="recipe_ingredients", on_delete=PROTECT)
    amount = m.FloatField()
    is_required = m.BooleanField(default=True)
    comment = m.TextField(blank=True)

    def __str__(self):
        return f"{self.ingredient.name} ({self.amount} {self.unit})"

    class Meta:
        ordering = ("order",)


@translate_model
class RecipeStep(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="steps", on_delete=CASCADE)
    name = m.CharField(max_length=63)
    order = m.PositiveSmallIntegerField()
    description = m.TextField(blank=True)
    photo = ThumbnailImageField(upload_to="recipe_steps", blank=True, null=True)

    class Meta:
        ordering = ("order",)


@translate_model
class RecipeTip(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="tips", on_delete=CASCADE)
    name = m.CharField(max_length=31)
    description = m.TextField()


@translate_model
class RecipeComment(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="comments", on_delete=CASCADE)
    user = m.ForeignKey(User, related_name="recipe_comments", on_delete=CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)
    comment = m.TextField()
