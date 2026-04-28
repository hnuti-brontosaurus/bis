from datetime import date

from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.db import models as m

from translation.translate import translate_model


@translate_model
class GrantCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class EventIntendedForCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class DietCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class QualificationCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)
    parents = m.ManyToManyField(
        "QualificationCategory", related_name="included_qualifications"
    )
    can_approve = m.ManyToManyField(
        "QualificationCategory", related_name="can_be_approved_with"
    )

    def get_slugs(self):
        yield self.slug
        for child in self.included_qualifications.all():
            yield from child.get_slugs()

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class AdministrationUnitCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class MembershipCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name

    @classmethod
    def get_individual(cls, birthday):
        if not birthday:
            return

        years = relativedelta(date(today().year, 1, 1), birthday).years
        if years < 15:
            return "kid"
        elif years <= 26:
            return "student"
        return "adult"

    @classmethod
    def get_extended(cls, user):
        if not user.birthday:
            return

        years = relativedelta(date(today().year, 1, 1), user.birthday).years
        if years < 15:
            slug = "kid"
        elif years <= 26:
            slug = "student"
        else:
            slug = "adult"

        return cls.objects.get(slug=slug)


@translate_model
class EventGroupCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class EventCategory(m.Model):
    name = m.CharField(max_length=63)
    description = m.TextField(blank=True)
    slug = m.SlugField(unique=True)
    order = m.PositiveSmallIntegerField(default=0)
    is_active = m.BooleanField(default=True)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.name


@translate_model
class EventTag(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)
    description = m.TextField(blank=True)
    is_active = m.BooleanField(default=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class EventProgramCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)
    email = m.EmailField()

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class DonationSourceCategory(m.Model):
    _import_id = m.CharField(max_length=7)
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class OrganizerRoleCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class TeamRoleCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class OpportunityCategory(m.Model):
    name = m.CharField(max_length=63)
    description = m.CharField(max_length=255)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.name} - {self.description}"


@translate_model
class OpportunityPriority(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class LocationProgramCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class LocationAccessibilityCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class RoleCategory(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class HealthInsuranceCompany(m.Model):
    name = m.CharField(max_length=127)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.slug} - {self.name}"


@translate_model
class PronounCategory(m.Model):
    name = m.CharField(max_length=127)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name

    @classmethod
    def get_variables(cls, user):
        slug = (user and user.pronoun and user.pronoun.slug) or "unknown"
        return {"m": slug == "man", "f": slug == "woman"}


@translate_model
class DonorEventCategory(m.Model):
    description = m.CharField(max_length=127)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.description
