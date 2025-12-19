from cookbook.models.base import BaseModel
from django.db.models import *
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
class RecipeTag(BaseCategory):
    pass
