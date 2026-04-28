from bis.models import User
from django.db import models as m
from django.db.models import CASCADE


class ChangeMixin(m.Model):
    created_at = m.DateTimeField(auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)
    created_by = m.ForeignKey(
        User, related_name="+", on_delete=CASCADE, null=True, blank=True
    )
    updated_by = m.ForeignKey(
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


class BaseModel(m.Model):
    class Meta:
        ordering = ("-id",)
        abstract = True

    def __str__(self):
        return getattr(self, "name", super().__str__())
