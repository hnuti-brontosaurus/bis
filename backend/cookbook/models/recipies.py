from bis.models import User
from common.thumbnails import ThumbnailImageField
from cookbook.models.base import BaseModel
from cookbook.models.categories import RecipeDifficulty, RecipeTag
from cookbook.models.chefs import Chef
from cookbook.models.units import Ingredient, Unit
from django.db.models import *
from translation.translate import translate_model


@translate_model
class Recipe(BaseModel):
    name = CharField(max_length=31)
    chef = ForeignKey(Chef, related_name="recipes", on_delete=PROTECT)
    difficulty = ForeignKey(RecipeDifficulty, related_name="recipes", on_delete=PROTECT)
    tags = ManyToManyField(RecipeTag, related_name="recipes", blank=True)
    photo = ThumbnailImageField(upload_to="recipes")
    intro = TextField()
    sources = TextField()
    is_public = BooleanField(default=False)


@translate_model
class RecipeIngredient(BaseModel):
    recipe = ForeignKey(Recipe, related_name="ingredients", on_delete=PROTECT)
    order = PositiveSmallIntegerField()
    ingredient = ForeignKey(
        Ingredient, related_name="recipe_ingredients", on_delete=PROTECT
    )
    unit = ForeignKey(Unit, related_name="recipe_ingredients", on_delete=PROTECT)
    amount = DecimalField(max_digits=10, decimal_places=1)
    is_optional = BooleanField(default=False)
    comment = TextField(blank=True)

    def __str__(self):
        return f"{self.ingredient.name} ({self.amount} {self.unit})"


@translate_model
class RecipeStep(BaseModel):
    recipe = ForeignKey(Recipe, related_name="steps", on_delete=PROTECT)
    name = CharField(max_length=63)
    order = PositiveSmallIntegerField()
    is_optional = BooleanField(default=False)
    description = TextField(blank=True)
    photo = ThumbnailImageField(upload_to="recipe_steps", blank=True, null=True)


@translate_model
class RecipeTip(BaseModel):
    recipe = ForeignKey(Recipe, related_name="tips", on_delete=PROTECT)
    name = CharField(max_length=31)
    description = TextField()


@translate_model
class RecipeComment(BaseModel):
    recipe = ForeignKey(Recipe, related_name="comments", on_delete=PROTECT)
    user = ForeignKey(User, related_name="recipe_comments", on_delete=PROTECT)
    created_at = DateTimeField(auto_now_add=True)
    comment = TextField()
