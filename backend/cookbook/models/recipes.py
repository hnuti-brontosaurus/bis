from bis.models import User
from common.thumbnails import ThumbnailImageField
from cookbook.models.base import BaseModel, ChangeMixin
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook_categories.models import (
    Allergen,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from django.core.validators import MinValueValidator
from django.db import models as m
from django.db.models import CASCADE, PROTECT
from tinymce.models import HTMLField
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
    intro = HTMLField(blank=True)
    sources = HTMLField(blank=True)
    default_servings = m.PositiveSmallIntegerField(
        default=2, validators=[MinValueValidator(1)]
    )
    servings_note = HTMLField(blank=True)
    difficulty_note = HTMLField(blank=True)
    is_public = m.BooleanField(default=False)
    # Denormalized cache of the allergens contributed by this recipe's
    # ingredients. Kept in sync by signals in cookbook.signals (whenever a
    # RecipeIngredient is added/removed, or an Ingredient's allergen set
    # changes). Read by the API; not editable per-recipe.
    allergens = m.ManyToManyField(Allergen, related_name="recipes", blank=True)

    def refresh_allergens(self):
        ids = (
            Allergen.objects.filter(ingredients__recipe_ingredients__recipe=self)
            .values_list("id", flat=True)
            .distinct()
        )
        self.allergens.set(list(ids))


@translate_model
class RecipeIngredient(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="ingredients", on_delete=CASCADE)
    order = m.PositiveSmallIntegerField()
    part = m.CharField(max_length=63, blank=True)
    ingredient = m.ForeignKey(
        Ingredient, related_name="recipe_ingredients", on_delete=PROTECT
    )
    unit = m.ForeignKey(Unit, related_name="recipe_ingredients", on_delete=PROTECT)
    amount = m.FloatField()
    is_optional = m.BooleanField(default=False)
    comment = HTMLField(blank=True)

    def __str__(self):
        return f"{self.ingredient.name} ({self.amount} {self.unit})"

    class Meta:
        ordering = ("order",)


@translate_model
class RecipeStep(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="steps", on_delete=CASCADE)
    name = m.CharField(max_length=63)
    order = m.PositiveSmallIntegerField()
    description = HTMLField(blank=True)
    is_optional = m.BooleanField(default=False)

    class Meta:
        ordering = ("order",)


class Photo(BaseModel):
    order = m.PositiveSmallIntegerField()

    class Meta:
        abstract = True
        ordering = ("order",)


@translate_model
class RecipePhoto(Photo):
    parent = m.ForeignKey(Recipe, related_name="photos", on_delete=CASCADE)
    photo = ThumbnailImageField(upload_to="recipes")


@translate_model
class RecipeIngredientPhoto(Photo):
    parent = m.ForeignKey(RecipeIngredient, related_name="photos", on_delete=CASCADE)
    photo = ThumbnailImageField(upload_to="recipe_ingredients")


@translate_model
class RecipeStepPhoto(Photo):
    parent = m.ForeignKey(RecipeStep, related_name="photos", on_delete=CASCADE)
    photo = ThumbnailImageField(upload_to="recipe_steps")


@translate_model
class RecipeTip(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="tips", on_delete=CASCADE)
    name = m.CharField(max_length=31)
    description = HTMLField()


@translate_model
class RecipeComment(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="comments", on_delete=CASCADE)
    user = m.ForeignKey(User, related_name="recipe_comments", on_delete=CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)
    comment = HTMLField()
