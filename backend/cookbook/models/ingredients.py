from django.db.models import *

from cookbook.models.base import BaseModel, ChangeMixin
from translation.translate import translate_model


@translate_model
class Ingredient(ChangeMixin, BaseModel):
    name = CharField(max_length=31, unique=True)
    state = CharField(
        max_length=13,
        choices=[("solid", "Pevná"), ("liquid", "Tekuté")],
        default="solid",
    )
    g_per_piece = PositiveSmallIntegerField(blank=True, null=True)
    g_per_liter = PositiveSmallIntegerField(blank=True, null=True)
    g_per_serving = PositiveSmallIntegerField(blank=True, null=True)
    reasoning = TextField(blank=True)
