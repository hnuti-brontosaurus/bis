from django.contrib.gis.db.models import *
from translation.translate import translate_model


@translate_model
class Region(Model):
    name = CharField(max_length=63)
    area = PolygonField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)


@translate_model
class ZipCode(Model):
    zip_code = CharField(max_length=5, unique=True)
    region = ForeignKey(
        Region, related_name="zip_code", on_delete=PROTECT, null=True, blank=True
    )

    def __str__(self):
        return self.zip_code

    class Meta:
        ordering = ("id",)
