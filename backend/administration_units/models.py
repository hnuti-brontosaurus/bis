from categories.models import AdministrationUnitCategory
from common.abstract_models import BaseAddress
from common.history import record_history
from common.thumbnails import ThumbnailImageField
from django.contrib.admin import display
from django.contrib.gis.db.models import *
from django.core.cache import cache
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel
from translation.translate import _, translate_model

from bis.helpers import SearchMixin, permission_cache, update_roles


@translate_model
class AdministrationUnit(SearchMixin, Model):
    name = CharField(max_length=255, unique=True)
    abbreviation = CharField(max_length=63, unique=True)
    description = TextField(blank=True, max_length=400)
    image = ThumbnailImageField(upload_to="administration_unit_images", blank=True)

    is_for_kids = BooleanField()

    phone = PhoneNumberField()
    email = EmailField()
    www = URLField(blank=True)
    facebook = URLField(blank=True)
    instagram = URLField(blank=True)
    ic = CharField(max_length=15, blank=True)
    bank_account_number = CharField(max_length=63, blank=True)
    data_box = CharField(max_length=63, blank=True)
    custom_statues = FileField(upload_to="custom_statues", blank=True)
    gps_location = PointField(null=True)

    existed_since = DateField(null=True)
    existed_till = DateField(null=True, blank=True)

    category = ForeignKey(
        AdministrationUnitCategory,
        related_name="administration_units",
        on_delete=PROTECT,
    )
    chairman = ForeignKey(
        "bis.User", related_name="chairman_of", on_delete=PROTECT, null=True
    )
    vice_chairman = ForeignKey(
        "bis.User",
        related_name="vice_chairman_of",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )
    manager = ForeignKey(
        "bis.User", related_name="manager_of", on_delete=PROTECT, null=True, blank=True
    )
    board_members = ManyToManyField(
        "bis.User", related_name="administration_units", blank=True
    )

    _import_id = CharField(max_length=15, default="")
    _history = JSONField(default=dict)
    _search_field = CharField(max_length=1024, blank=True)
    search_fields = [
        "abbreviation",
        "name",
        "address__city",
        "address__street",
        "address__zip_code",
        "phone",
        "email",
    ]

    def clean(self):
        if self.existed_till is not None:
            return

        if not self.manager and not self.category.slug == "club":
            raise ValidationError("Hospodář není povinný pouze pro kluby")

    @update_roles("chairman", "vice_chairman", "manager")
    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not cache.get("skip_validation"):
            self.clean()
        self.email = self.email.lower()
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = (
            "-existed_till",
            "abbreviation",
        )
        indexes = [Index(fields=["-existed_till", "abbreviation"])]

    def __str__(self):
        return self.abbreviation

    def record_history(self, date):
        record_history(self._history, date, self.chairman, "Předseda")
        record_history(self._history, date, self.vice_chairman, "Místopředseda")
        record_history(self._history, date, self.manager, "Hospodář")
        for user in self.board_members.all():
            if user not in [self.chairman, self.vice_chairman, self.manager]:
                record_history(self._history, date, user, "Člen představenstva")

        AdministrationUnit.objects.bulk_update([self], ["_history"])

        for sub_unit in self.sub_units.all():
            sub_unit.record_history(date)

    @permission_cache
    def has_edit_permission(self, user):
        return user in self.board_members.all()

    @display(description="Je aktivní", boolean=True)
    def is_active(self):
        return self.existed_till is None


@translate_model
class AdministrationUnitAddress(BaseAddress):
    administration_unit = OneToOneField(
        AdministrationUnit, on_delete=CASCADE, related_name="address"
    )


@translate_model
class AdministrationUnitContactAddress(BaseAddress):
    administration_unit = OneToOneField(
        AdministrationUnit, on_delete=CASCADE, related_name="contact_address"
    )


@translate_model
class GeneralMeeting(Model):
    administration_unit = ForeignKey(
        AdministrationUnit, related_name="general_meetings", on_delete=CASCADE
    )

    date = DateField()
    place = CharField(max_length=63)

    def __str__(self):
        return f"Valná hromada {self.place} - {self.date}"

    class Meta:
        ordering = ("date",)


@translate_model
class AdministrationSubUnit(Model):
    administration_unit = ForeignKey(
        AdministrationUnit, related_name="sub_units", on_delete=PROTECT
    )
    name = CharField(max_length=255, unique=True)
    description = TextField(blank=True, max_length=400)

    is_for_kids = BooleanField()
    is_active = BooleanField(default=True)

    phone = PhoneNumberField()
    email = EmailField()
    www = URLField(blank=True)
    facebook = URLField(blank=True)
    instagram = URLField(blank=True)
    gps_location = PointField(null=True)
    _history = JSONField(default=dict)

    main_leader = ForeignKey(
        "bis.User", related_name="main_leader_of", on_delete=PROTECT
    )
    sub_leaders = ManyToManyField("bis.User", related_name="sub_leader_of", blank=True)

    class Meta:
        ordering = ("name",)
        indexes = [Index(fields=["name"])]

    def __str__(self):
        return self.name

    def record_history(self, date):
        record_history(self._history, date, self.main_leader, "Hlavní vedoucí")
        for user in self.sub_leaders.all():
            record_history(self._history, date, user, "Oddílový vedoucí")

        AdministrationSubUnit.objects.bulk_update([self], ["_history"])

    @permission_cache
    def has_edit_permission(self, user):
        return self.administration_unit.has_edit_permission(user)


@translate_model
class AdministrationSubUnitAddress(BaseAddress):
    sub_unit = OneToOneField(
        AdministrationSubUnit, on_delete=CASCADE, related_name="address"
    )


@translate_model
class BrontosaurusMovement(SingletonModel):
    director = ForeignKey("bis.User", related_name="director_of", on_delete=PROTECT)
    finance_director = ForeignKey(
        "bis.User", related_name="finance_director_of", on_delete=PROTECT
    )
    bis_administrators = ManyToManyField("bis.User", related_name="+", blank=True)
    office_workers = ManyToManyField("bis.User", related_name="+", blank=True)
    audit_committee = ManyToManyField("bis.User", related_name="+", blank=True)
    executive_committee = ManyToManyField("bis.User", related_name="+", blank=True)
    education_members = ManyToManyField("bis.User", related_name="+", blank=True)
    _history = JSONField(default=dict)

    @update_roles("director", "finance_director")
    def save(self, *args, **kwargs):
        cache.set("brontosaurus_movement", None)
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj = cache.get("brontosaurus_movement")
        if not obj:
            obj = cls.objects.get()
            cache.set("brontosaurus_movement", obj)

        return obj

    def __str__(self):
        return _("models.BrontosaurusMovement.name")

    def record_history(self, date):
        record_history(self._history, date, self.director, "Ředitel")
        record_history(self._history, date, self.finance_director, "Finanční ředitel")
        for user in self.bis_administrators.all():
            record_history(self._history, date, user, "Správce BISu")
        for user in self.office_workers.all():
            record_history(self._history, date, user, "Člen ústředí")
        for user in self.audit_committee.all():
            record_history(self._history, date, user, "KRK")
        for user in self.executive_committee.all():
            record_history(self._history, date, user, "VV")
        for user in self.education_members.all():
            record_history(self._history, date, user, "EDU")

        self.save()
