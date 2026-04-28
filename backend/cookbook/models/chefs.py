from django.db import models as m
from django.db.models import PROTECT

from bis.models import User
from common.thumbnails import ThumbnailImageField
from cookbook.models.base import BaseModel, ChangeMixin
from translation.translate import translate_model


@translate_model
class Chef(ChangeMixin, BaseModel):
    user = m.OneToOneField(User, related_name="chef", on_delete=PROTECT)
    name = m.CharField(max_length=31)
    email = m.EmailField()
    photo = ThumbnailImageField(upload_to="chefs")
    is_editor = m.BooleanField(default=False)
