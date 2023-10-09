from datetime import date

from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.db.models import *

from translation.translate import translate_model


@translate_model
class GrantCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class EventIntendedForCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class DietCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class QualificationCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)
    parents = ManyToManyField('QualificationCategory', related_name='included_qualifications')
    can_approve = ManyToManyField('QualificationCategory', related_name='can_be_approved_with')

    def get_slugs(self):
        yield self.slug
        for child in self.included_qualifications.all():
            yield from child.get_slugs()

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class AdministrationUnitCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class MembershipCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)
    price = PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name

    @classmethod
    def get_individual(cls, user):
        if not user.birthday:
            return

        years = relativedelta(date(today().year, 1, 1), user.birthday).years
        if years < 15: return 'kid'
        elif years <= 26: return 'student'
        return 'adult'

    @classmethod
    def get_extended(cls, user):
        if not user.birthday:
            return



        years = relativedelta(date(today().year, 1, 1), user.birthday).years
        if years < 15: slug = 'kid'
        elif years <= 26: slug = 'student'
        else: slug = 'adult'

        return cls.objects.get(slug=slug)


@translate_model
class EventGroupCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class EventCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class EventProgramCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class DonationSourceCategory(Model):
    _import_id = CharField(max_length=7)
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class OrganizerRoleCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class TeamRoleCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class OpportunityCategory(Model):
    name = CharField(max_length=63)
    description = CharField(max_length=255)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f"{self.name} - {self.description}"


@translate_model
class LocationProgramCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class LocationAccessibilityCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class RoleCategory(Model):
    name = CharField(max_length=63)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name


@translate_model
class HealthInsuranceCompany(Model):
    name = CharField(max_length=127)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f"{self.slug} - {self.name}"


@translate_model
class PronounCategory(Model):
    name = CharField(max_length=127)
    slug = SlugField(unique=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return self.name

    @classmethod
    def get_variables(cls, user):
        slug = (user and user.pronoun and user.pronoun.slug) or 'unknown'
        return {"m": slug == 'man', "f": slug == 'female'}