from django.db.models import *

from bis.models import User
from common.thumbnails import ThumbnailImageField
from cookbook.models.base import BaseModel, ChangeMixin
from translation.translate import translate_model


@translate_model
class Chef(ChangeMixin, BaseModel):
    user = OneToOneField(User, related_name="chef", on_delete=PROTECT)
    name = CharField(max_length=31)
    email = EmailField()
    photo = ThumbnailImageField(upload_to="chefs")
    is_editor = BooleanField(default=False)
