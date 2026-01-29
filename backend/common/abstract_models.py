import re

from django.apps import apps
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import PROTECT, CharField, EmailField, ForeignKey, Model
from django.db.models.functions import Length
from phonenumber_field.modelfields import PhoneNumberField

from translation.translate import translate_model

CharField.register_lookup(Length)


@translate_model
class BaseContact(Model):
    first_name = CharField(max_length=63)
    last_name = CharField(max_length=63)
    phone = PhoneNumberField(blank=True)
    email = EmailField(blank=True)

    def clean(self):
        if not self.phone and not self.email:
            raise ValidationError("Je třeba vyplnit e-mail nebo telefon")

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not cache.get("skip_validation"):
            self.clean()
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ("id",)
        abstract = True

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


@translate_model
class BaseAddress(Model):
    street = CharField(max_length=127)
    city = CharField(max_length=63)
    zip_code = CharField(max_length=5)
    region = ForeignKey(
        "regions.Region", related_name="+", on_delete=PROTECT, null=True, blank=True
    )

    class Meta:
        ordering = ("id",)
        abstract = True

    def __str__(self):
        return f"{self.street}, {self.city}, {self.zip_code}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.zip_code = re.sub(r"\s+", "", str(self.zip_code))[:5]
        zip_code = (
            apps.get_model("regions", "ZipCode")
            .objects.filter(zip_code=self.zip_code)
            .first()
        )
        if zip_code and zip_code.region:
            self.region = zip_code.region
        super().save(force_insert, force_update, using, update_fields)
