from django.contrib.gis.db import models as m
from django.db.models import PROTECT
from translation.translate import translate_model


@translate_model
class Region(m.Model):
    name = m.CharField(max_length=63)
    area = m.PolygonField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)


@translate_model
class ZipCode(m.Model):
    zip_code = m.CharField(max_length=5, unique=True)
    region = m.ForeignKey(
        Region, related_name="zip_code", on_delete=PROTECT, null=True, blank=True
    )

    def __str__(self):
        return self.zip_code

    class Meta:
        ordering = ("id",)
