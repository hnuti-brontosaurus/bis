from django.db import models as m
from translation.translate import translate_model


@translate_model
class BaseCategory(m.Model):
    name = m.CharField(max_length=30)
    slug = m.SlugField()
    description = m.CharField(max_length=120, blank=True)
    emoji = m.CharField(max_length=3)

    class Meta:
        ordering = ("id",)
        abstract = True

    def __str__(self):
        return f"{self.emoji} {self.name}"


@translate_model
class Tag(BaseCategory):
    name = m.CharField(max_length=15)


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
