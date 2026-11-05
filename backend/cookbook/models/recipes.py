from os.path import basename

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
from django.db import transaction
from django.db.models import CASCADE, PROTECT, SET_NULL
from django.utils.html import escape
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
    original = m.ForeignKey(
        "self", related_name="copies", on_delete=SET_NULL, null=True, blank=True
    )
    # Denormalized cache of the allergens contributed by this recipe's
    # non-optional ingredients. Kept in sync by signals in cookbook.signals
    # (whenever a RecipeIngredient is saved/removed, or an Ingredient's
    # allergen set changes). Read by the API; not editable per-recipe.
    allergens = m.ManyToManyField(Allergen, related_name="recipes", blank=True)

    def refresh_allergens(self):
        ids = (
            Allergen.objects.filter(
                ingredients__recipe_ingredients__recipe=self,
                ingredients__recipe_ingredients__is_optional=False,
            )
            .values_list("id", flat=True)
            .distinct()
        )
        self.allergens.set(list(ids))

    COPY_SUFFIX = " - kopie"

    @transaction.atomic
    def duplicate(self, chef):
        """A private copy for `chef`, photos included: the copy is meant to
        be edited into the chef's own version, and published only once it
        differs enough, see the cookbook's duplicate dialog."""
        name_length = self._meta.get_field("name").max_length - len(self.COPY_SUFFIX)
        link = f'<a href="/kucharka/recept/{self.id}/">{escape(self.name)}</a>'
        copy = Recipe.objects.create(
            name=self.name[:name_length].rstrip() + self.COPY_SUFFIX,
            chef=chef,
            original=self,
            difficulty=self.difficulty,
            required_time=self.required_time,
            intro=self.intro,
            sources=f"{self.sources}<p>Původní recept: {link}</p>",
            default_servings=self.default_servings,
            servings_note=self.servings_note,
            difficulty_note=self.difficulty_note,
        )
        copy.tags.set(self.tags.all())
        copy_photos(self.photos.all(), copy)
        for related_name in ("ingredients", "steps", "tips"):
            for row in getattr(self, related_name).all():
                photos = list(row.photos.all())
                row.pk = None
                row._state.adding = True
                row.recipe = copy
                row.save()
                copy_photos(photos, row)
        return copy


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
    order = m.PositiveSmallIntegerField()
    description = HTMLField()

    class Meta:
        ordering = ("order",)


@translate_model
class RecipeTipPhoto(Photo):
    parent = m.ForeignKey(RecipeTip, related_name="photos", on_delete=CASCADE)
    photo = ThumbnailImageField(upload_to="recipe_tips")


@translate_model
class RecipeComment(BaseModel):
    recipe = m.ForeignKey(Recipe, related_name="comments", on_delete=CASCADE)
    user = m.ForeignKey(User, related_name="recipe_comments", on_delete=CASCADE)
    created_at = m.DateTimeField(auto_now_add=True)
    comment = HTMLField()
    # A private comment is shared with the recipe's author only.
    is_public = m.BooleanField(default=True)


@translate_model
class RecipeCommentPhoto(Photo):
    parent = m.ForeignKey(RecipeComment, related_name="photos", on_delete=CASCADE)
    photo = ThumbnailImageField(upload_to="recipe_comments")


@translate_model
class RecipeNote(BaseModel):
    """A user's own note on a recipe, seen by nobody else."""

    recipe = m.ForeignKey(Recipe, related_name="notes", on_delete=CASCADE)
    user = m.ForeignKey(User, related_name="recipe_notes", on_delete=CASCADE)
    note = HTMLField(blank=True)

    class Meta(BaseModel.Meta):
        constraints = [
            m.UniqueConstraint(fields=["recipe", "user"], name="one_note_per_recipe")
        ]


@translate_model
class RecipeNotePhoto(Photo):
    parent = m.ForeignKey(RecipeNote, related_name="photos", on_delete=CASCADE)
    photo = ThumbnailImageField(upload_to="recipe_notes")


def copy_photos(photos, target):
    """Copies the files too: django_cleanup deletes a file with the row that
    holds it, without checking whether another row shares it."""
    for photo in photos:
        copy = type(photo)(parent=target, order=photo.order)
        copy.photo.save(basename(photo.photo.name), photo.photo.file)
