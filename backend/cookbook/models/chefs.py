from common.thumbnails import ThumbnailImageField
from cookbook.models.base import BaseModel, ChangeMixin
from django.db.models import *
from translation.translate import translate_model

from bis.models import User


@translate_model
class Chef(ChangeMixin, BaseModel):
    user = OneToOneField(User, related_name="chef", on_delete=PROTECT)
    name = CharField(max_length=31)
    email = EmailField()
    photo = ThumbnailImageField(upload_to="chefs")
    is_editor = BooleanField(default=False)
