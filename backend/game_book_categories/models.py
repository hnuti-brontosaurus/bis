from django.db.models import *
from translation.translate import translate_model


@translate_model
class BaseCategory(Model):
    name = CharField(max_length=30)
    slug = SlugField()
    description = CharField(max_length=120, blank=True)
    emoji = CharField(max_length=3)

    class Meta:
        ordering = ("id",)
        abstract = True

    def __str__(self):
        return f"{self.emoji} {self.name}"


@translate_model
class Tag(BaseCategory):
    name = CharField(max_length=15)


@translate_model
class PhysicalCategory(BaseCategory):
    pass


@translate_model
class MentalCategory(BaseCategory):
    pass


@translate_model
class LocationCategory(BaseCategory):
    pass


@translate_model
class ParticipantNumberCategory(BaseCategory):
    pass


@translate_model
class ParticipantAgeCategory(BaseCategory):
    pass


@translate_model
class GameLengthCategory(BaseCategory):
    pass


@translate_model
class PreparationLengthCategory(BaseCategory):
    pass


@translate_model
class OrganizersNumberCategory(BaseCategory):
    pass


@translate_model
class MaterialRequirementCategory(BaseCategory):
    pass
