from django.db.models import *

from bis.models import User
from common.thumbnails import ThumbnailImageField
from translation.translate import translate_model


class ChangeMixin(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    created_by = ForeignKey(
        User, related_name="+", on_delete=CASCADE, null=True, blank=True
    )
    updated_by = ForeignKey(
        User, related_name="+", on_delete=CASCADE, null=True, blank=True
    )
    fields = [
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]

    class Meta:
        abstract = True


class BaseModel(Model):
    class Meta:
        ordering = ("-id",)
        abstract = True

    def __str__(self):
        return getattr(self, "name", super().__str__())
