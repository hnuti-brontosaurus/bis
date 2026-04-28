from administration_units.models import AdministrationUnit
from bis.helpers import filter_queryset_with_multiple_or_queries, permission_cache
from bis.models import User
from categories.models import DonationSourceCategory, DonorEventCategory
from dateutil.utils import today
from django.contrib.gis.db import models as m
from django.db.models import CASCADE, PROTECT, Index, Q, TextChoices
from solo.models import SingletonModel
from translation.translate import translate_model


def get_today():
    return today().date()


@translate_model
class Donor(m.Model):
    user = m.OneToOneField(User, related_name="donor", on_delete=PROTECT)
    formal_vokativ = m.CharField(max_length=63, blank=True)
    subscribed_to_newsletter = m.BooleanField(default=True)
    is_public = m.BooleanField(default=True)
    fundraisers_note = m.TextField(blank=True)
    do_not_call = m.BooleanField(default=False)
    do_not_solicit = m.BooleanField(default=False)

    date_joined = m.DateField(default=get_today)
    regional_center_support = m.ForeignKey(
        AdministrationUnit,
        related_name="supported_as_regional_center",
        on_delete=PROTECT,
        null=True,
        blank=True,
        limit_choices_to={"category__slug": "regional_center"},
    )
    basic_section_support = m.ForeignKey(
        AdministrationUnit,
        related_name="supported_as_basic_section",
        on_delete=PROTECT,
        null=True,
        blank=True,
        limit_choices_to={"category__slug": "basic_section"},
    )

    def __str__(self):
        return f"{self.user}"

    class Meta:
        ordering = ("-date_joined",)
        Index(fields=["date_joined"])

    def merge_with(self, other):
        assert other != self
        for field in self._meta.fields:
            if field.name in ["id", "subscribed_to_newsletter", "is_public", "user"]:
                continue

            elif field.name in ["do_not_call", "do_not_solicit"]:
                if getattr(other, field.name):
                    setattr(self, field.name, True)

            elif field.name in [
                "regional_center_support",
                "basic_section_support",
                "fundraisers_note",
                "formal_vokativ",
            ]:
                if not getattr(self, field.name) and getattr(other, field.name):
                    setattr(self, field.name, getattr(other, field.name))

            elif field.name in [
                "date_joined",
            ]:
                if getattr(other, field.name) < getattr(self, field.name):
                    setattr(self, field.name, getattr(other, field.name))
            else:
                raise RuntimeError(
                    f"field {field.name} not checked, database was updated, merge is outdated"
                )

        for relation in self._meta.related_objects:
            if isinstance(relation, (m.ManyToOneRel, m.OneToOneRel)):
                for obj in relation.field.model.objects.filter(
                    **{relation.field.name: other}
                ):
                    setattr(obj, relation.field.name, self)
                    obj.save()

            elif isinstance(relation, m.ManyToManyRel):
                for obj in relation.field.model.objects.filter(
                    **{relation.field.name: other}
                ):
                    getattr(obj, relation.field.name).add(self)
                    getattr(obj, relation.field.name).remove(other)

        self.save()
        other.delete()

    @classmethod
    def filter_queryset(cls, queryset, perm):
        queries = [Q(user=perm.user)]
        if perm.user.is_board_member:
            queries += [
                Q(regional_center_support__in=perm.user.administration_units.all()),
                Q(basic_section_support__in=perm.user.administration_units.all()),
            ]

        return filter_queryset_with_multiple_or_queries(queryset, queries)

    @permission_cache
    def has_edit_permission(self, user):
        return (
            self.user == user
            or self.regional_center_support in user.administration_units.all()
            or self.basic_section_support in user.administration_units.all()
        )

    def has_active_recurrent_donation(self):
        return self.pledges.filter(
            is_recurrent=True, recurrent_state="collecting"
        ).exists()

    def had_recurrent_donation(self):
        return self.pledges.filter(
            is_recurrent=True, recurrent_state="stopped"
        ).exists()


@translate_model
class Company(m.Model):
    donor = m.OneToOneField(Donor, related_name="company", on_delete=CASCADE)
    name = m.CharField(max_length=255)
    ico = m.CharField(max_length=15)
    address = m.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)


@translate_model
class VariableSymbol(m.Model):
    donor = m.ForeignKey(Donor, related_name="variable_symbols", on_delete=CASCADE)
    variable_symbol = m.PositiveBigIntegerField(unique=True)

    def __str__(self):
        return str(self.variable_symbol)

    class Meta:
        ordering = ("id",)


class RecurrentState(TextChoices):
    UNKNOWN = "unknown"
    ONE_TIME = "one_time"
    STOPPED = "stopped"
    COLLECTING = "collecting"


@translate_model
class Pledge(m.Model):
    """Only for donations from Darujme API."""

    id = m.PositiveIntegerField(primary_key=True)  # comes from Darujme API

    donor = m.ForeignKey(Donor, on_delete=PROTECT, related_name="pledges")

    donation_source = m.ForeignKey(
        DonationSourceCategory,
        on_delete=PROTECT,
        related_name="pledges",
    )

    is_recurrent = m.BooleanField(default=False)
    recurrent_state = m.CharField(
        max_length=32,
        choices=RecurrentState.choices,
        default=RecurrentState.UNKNOWN,
    )
    pledged_at = m.DateField()

    class Meta:
        ordering = ("-pledged_at",)


@translate_model
class FundraisingCampaign(m.Model):
    name = m.CharField(max_length=63)
    slug = m.SlugField(unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


@translate_model
class DonorEvent(m.Model):
    donor = m.ForeignKey(Donor, on_delete=CASCADE, related_name="events")
    event_type = m.ForeignKey(DonorEventCategory, on_delete=PROTECT)
    created_at = m.DateTimeField(auto_now_add=True)
    campaign = m.ForeignKey(
        FundraisingCampaign,
        on_delete=PROTECT,
        related_name="events",
    )
    fundraisers_note = m.TextField(blank=True)
    pledge = m.TextField(blank=True)
    reminder = m.DateTimeField(null=True, blank=True)
    created_by = m.ForeignKey(
        User,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )


@translate_model
class Donation(m.Model):
    donor = m.ForeignKey(Donor, on_delete=PROTECT, related_name="donations", null=True)
    pledge = m.ForeignKey(Pledge, null=True, blank=True, on_delete=PROTECT)

    donated_at = m.DateField()
    amount = m.IntegerField()
    donation_source = m.ForeignKey(
        DonationSourceCategory, related_name="donations", on_delete=PROTECT
    )

    _variable_symbol = m.PositiveBigIntegerField(null=True)
    _import_id = m.PositiveIntegerField(null=True)
    info = m.TextField()

    def __str__(self):
        return f"{self.amount} Kč"

    class Meta:
        ordering = ("-donated_at",)
        Index(fields=["donated_at"])

    @classmethod
    def filter_queryset(cls, queryset, perm):
        return filter_queryset_with_multiple_or_queries(
            queryset,
            [
                Q(
                    donor__regional_center_support__in=perm.user.administration_units.all()
                ),
                Q(
                    donor__basic_section_support__in=perm.user.administration_units.all()
                ),
            ],
        )


@translate_model
class UploadBankRecords(SingletonModel):
    file = m.FileField(upload_to="bank_records")

    def __str__(self):
        return "Nahrání bankovního záznamu"

    class Meta:
        ordering = ("id",)
