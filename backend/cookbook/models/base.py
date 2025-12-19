from bis.models import User
from common.thumbnails import ThumbnailImageField
from django.db.models import *
from translation.translate import translate_model


class BaseModel(Model):
    class Meta:
        ordering = ("-id",)
        abstract = True

    def __str__(self):
        return getattr(self, "name", super().__str__())
