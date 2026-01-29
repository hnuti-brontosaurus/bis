from django.db.models import *
from django.db.models import CharField, SlugField

from cookbook.models.base import BaseModel
from translation.translate import translate_model


class BaseCategory(BaseModel):
    name = CharField(max_length=31)
    slug = SlugField()
    order = PositiveSmallIntegerField()

    class Meta:
        ordering = ("order",)
        abstract = True


@translate_model
class RecipeDifficulty(BaseCategory):
    pass


@translate_model
class RecipeRequiredTime(BaseCategory):
    pass


@translate_model
class RecipeTag(BaseCategory):
    group = CharField(max_length=31)


@translate_model
class Unit(BaseCategory):
    name2 = CharField(max_length=31)
    name5 = CharField(max_length=31)
    abbreviation = CharField(max_length=7, blank=True)
    of = CharField(
        max_length=15,
        choices=[
            ("weight", "Váha"),
            ("volume", "Objem"),
            ("pieces", "Kus"),
            ("servings", "Porce"),
        ],
    )
