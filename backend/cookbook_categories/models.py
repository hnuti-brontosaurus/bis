from django.db.models import *
from translation.translate import translate_model


class BaseCategory(Model):
    name = CharField(max_length=31)
    slug = SlugField()
    order = PositiveSmallIntegerField()

    class Meta:
        ordering = ("order",)
        abstract = True

    def __str__(self):
        return getattr(self, "name", super().__str__())


@translate_model
class RecipeDifficulty(BaseCategory):
    pass


@translate_model
class RecipeTimeRequired(BaseCategory):
    pass


@translate_model
class RecipeDietRestriction(BaseCategory):
    pass


@translate_model
class RecipeCourse(BaseCategory):
    pass


@translate_model
class RecipeType(BaseCategory):
    group = CharField(max_length=31, blank=True)
    pass


@translate_model
class RecipeTag(BaseCategory):
    pass
