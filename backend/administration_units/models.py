from bis.helpers import SearchMixin, permission_cache, update_roles
from categories.models import AdministrationUnitCategory
from common.abstract_models import BaseAddress
from common.history import record_history
from common.thumbnails import ThumbnailImageField
from django.contrib.admin import display
from django.contrib.gis.db import models as m
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import CASCADE, PROTECT, Index
from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel
from translation.translate import _, translate_model


@translate_model
class AdministrationUnit(SearchMixin, m.Model):
    name = m.CharField(max_length=255, unique=True)
    abbreviation = m.CharField(max_length=63, unique=True)
    description = m.TextField(blank=True, max_length=400)
    image = ThumbnailImageField(upload_to="administration_unit_images", blank=True)

    is_for_kids = m.BooleanField()

    phone = PhoneNumberField()
    email = m.EmailField()
    www = m.URLField(blank=True)
    facebook = m.URLField(blank=True)
    instagram = m.URLField(blank=True)
    ic = m.CharField(max_length=15, blank=True)
    bank_account_number = m.CharField(max_length=63, blank=True)
    data_box = m.CharField(max_length=63, blank=True)
    custom_statues = m.FileField(upload_to="custom_statues", blank=True)
    gps_location = m.PointField(null=True)

    existed_since = m.DateField(null=True)
    existed_till = m.DateField(null=True, blank=True)

    category = m.ForeignKey(
        AdministrationUnitCategory,
        related_name="administration_units",
        on_delete=PROTECT,
    )
    chairman = m.ForeignKey(
        "bis.User", related_name="chairman_of", on_delete=PROTECT, null=True
    )
    vice_chairman = m.ForeignKey(
        "bis.User",
        related_name="vice_chairman_of",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )
    manager = m.ForeignKey(
        "bis.User",
        related_name="manager_of",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )
    board_members = m.ManyToManyField(
        "bis.User", related_name="administration_units", blank=True
    )

    _import_id = m.CharField(max_length=15, default="")
    _history = m.JSONField(default=dict)
    _search_field = m.CharField(max_length=1024, blank=True)
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
    administration_unit = m.OneToOneField(
        AdministrationUnit, on_delete=CASCADE, related_name="address"
    )


@translate_model
class AdministrationUnitContactAddress(BaseAddress):
    administration_unit = m.OneToOneField(
        AdministrationUnit, on_delete=CASCADE, related_name="contact_address"
    )


@translate_model
class GeneralMeeting(m.Model):
    administration_unit = m.ForeignKey(
        AdministrationUnit, related_name="general_meetings", on_delete=CASCADE
    )

    date = m.DateField()
    place = m.CharField(max_length=63)

    def __str__(self):
        return f"Valná hromada {self.place} - {self.date}"

    class Meta:
        ordering = ("date",)


@translate_model
class AdministrationSubUnit(m.Model):
    administration_unit = m.ForeignKey(
        AdministrationUnit, related_name="sub_units", on_delete=PROTECT
    )
    name = m.CharField(max_length=255, unique=True)
    description = m.TextField(blank=True, max_length=400)

    is_for_kids = m.BooleanField()
    is_active = m.BooleanField(default=True)

    phone = PhoneNumberField()
    email = m.EmailField()
    www = m.URLField(blank=True)
    facebook = m.URLField(blank=True)
    instagram = m.URLField(blank=True)
    gps_location = m.PointField(null=True)
    _history = m.JSONField(default=dict)

    main_leader = m.ForeignKey(
        "bis.User", related_name="main_leader_of", on_delete=PROTECT
    )
    sub_leaders = m.ManyToManyField(
        "bis.User", related_name="sub_leader_of", blank=True
    )

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
    sub_unit = m.OneToOneField(
        AdministrationSubUnit, on_delete=CASCADE, related_name="address"
    )


@translate_model
class BrontosaurusMovement(SingletonModel):
    director = m.ForeignKey("bis.User", related_name="director_of", on_delete=PROTECT)
    finance_director = m.ForeignKey(
        "bis.User", related_name="finance_director_of", on_delete=PROTECT
    )
    bis_administrators = m.ManyToManyField("bis.User", related_name="+", blank=True)
    office_workers = m.ManyToManyField("bis.User", related_name="+", blank=True)
    audit_committee = m.ManyToManyField("bis.User", related_name="+", blank=True)
    executive_committee = m.ManyToManyField("bis.User", related_name="+", blank=True)
    education_members = m.ManyToManyField("bis.User", related_name="+", blank=True)
    fundraisers = m.ManyToManyField("bis.User", related_name="+", blank=True)
    _history = m.JSONField(default=dict)

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
        for user in self.fundraisers.all():
            record_history(self._history, date, user, "Fundraiser")

        self.save()
