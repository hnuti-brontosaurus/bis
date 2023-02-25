from django.conf import settings
from django.contrib.gis.db.models import *
from django.core.cache import cache
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel

from bis.helpers import permission_cache, update_roles
from categories.models import AdministrationUnitCategory
from common.abstract_models import BaseAddress
from common.history import record_history
from translation.translate import translate_model, _


@translate_model
class AdministrationUnit(Model):
    name = CharField(max_length=255, unique=True)
    abbreviation = CharField(max_length=63, unique=True)

    is_for_kids = BooleanField()

    phone = PhoneNumberField()
    email = EmailField()
    www = URLField(blank=True)
    facebook = URLField(blank=True)
    instagram = URLField(blank=True)
    ic = CharField(max_length=15, blank=True)
    bank_account_number = CharField(max_length=63, blank=True)
    data_box = CharField(max_length=63, blank=True)
    custom_statues = FileField(upload_to='custom_statues', blank=True)
    gps_location = PointField(null=True)

    existed_since = DateField(null=True)
    existed_till = DateField(null=True, blank=True)

    category = ForeignKey(AdministrationUnitCategory, related_name='administration_units', on_delete=PROTECT)
    chairman = ForeignKey('bis.User', related_name='chairman_of', on_delete=PROTECT, null=True)
    vice_chairman = ForeignKey('bis.User', related_name='vice_chairman_of', on_delete=PROTECT, null=True, blank=True)
    manager = ForeignKey('bis.User', related_name='manager_of', on_delete=PROTECT, null=True, blank=True)
    board_members = ManyToManyField('bis.User', related_name='administration_units', blank=True)

    _import_id = CharField(max_length=15, default='')
    _history = JSONField(default=dict)

    def clean(self):
        if not self.manager and not self.category.slug == "club":
            raise ValidationError('Hospodář není povinný pouze pro kluby')

    @update_roles('chairman', 'vice_chairman', 'manager')
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not settings.SKIP_VALIDATION: self.clean()
        self.email = self.email.lower()
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = 'abbreviation',

    def __str__(self):
        return self.abbreviation

    def record_history(self, date):
        record_history(self._history, date, self.chairman, "Předseda")
        record_history(self._history, date, self.vice_chairman, 'Místopředseda')
        record_history(self._history, date, self.manager, 'Hospodář')
        for user in self.board_members.all():
            if user not in [self.chairman, self.vice_chairman, self.manager]:
                record_history(self._history, date, user, 'Člen představenstva')

        self.save()

    @permission_cache
    def has_edit_permission(self, user):
        return user in self.board_members.all()


@translate_model
class AdministrationUnitAddress(BaseAddress):
    administration_unit = OneToOneField(AdministrationUnit, on_delete=CASCADE, related_name='address')


@translate_model
class AdministrationUnitContactAddress(BaseAddress):
    administration_unit = OneToOneField(AdministrationUnit, on_delete=CASCADE, related_name='contact_address')


@translate_model
class GeneralMeeting(Model):
    administration_unit = ForeignKey(AdministrationUnit, related_name='general_meetings', on_delete=CASCADE)

    date = DateField()
    place = CharField(max_length=63)

    def __str__(self):
        return f"Valná hromada {self.place} - {self.date}"

    class Meta:
        ordering = 'date',


@translate_model
class BrontosaurusMovement(SingletonModel):
    director = ForeignKey('bis.User', related_name='director_of', on_delete=PROTECT)
    finance_director = ForeignKey('bis.User', related_name='finance_director_of', on_delete=PROTECT)
    bis_administrators = ManyToManyField('bis.User', related_name='+', blank=True)
    office_workers = ManyToManyField('bis.User', related_name='+', blank=True)
    audit_committee = ManyToManyField('bis.User', related_name='+', blank=True)
    executive_committee = ManyToManyField('bis.User', related_name='+', blank=True)
    education_members = ManyToManyField('bis.User', related_name='+', blank=True)
    _history = JSONField(default=dict)

    @update_roles('director', 'finance_director')
    def save(self, *args, **kwargs):
        cache.set('brontosaurus_movement', None)
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj = cache.get('brontosaurus_movement')
        if not obj:
            obj = cls.objects.get()
            cache.set('brontosaurus_movement', obj)

        return obj

    def __str__(self):
        return _('models.BrontosaurusMovement.name')

    def record_history(self, date):
        record_history(self._history, date, self.director, "Ředitel")
        record_history(self._history, date, self.finance_director, 'Finanční ředitel')
        for user in self.bis_administrators.all():
            record_history(self._history, date, user, 'Správce BISu')
        for user in self.office_workers.all():
            record_history(self._history, date, user, 'Člen ústředí')
        for user in self.audit_committee.all():
            record_history(self._history, date, user, 'KRK')
        for user in self.executive_committee.all():
            record_history(self._history, date, user, 'VV')
        for user in self.education_members.all():
            record_history(self._history, date, user, 'EDU')

        self.save()
