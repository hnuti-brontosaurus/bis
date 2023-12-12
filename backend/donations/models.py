from administration_units.models import AdministrationUnit
from bis.helpers import filter_queryset_with_multiple_or_queries, permission_cache
from bis.models import User
from categories.models import DonationSourceCategory
from dateutil.utils import today
from django.contrib.gis.db.models import *
from solo.models import SingletonModel
from translation.translate import translate_model


def get_today():
    return today().date()


@translate_model
class Donor(Model):
    user = OneToOneField(User, related_name="donor", on_delete=PROTECT)
    subscribed_to_newsletter = BooleanField(default=True)
    is_public = BooleanField(default=True)
    has_recurrent_donation = BooleanField(default=False)
    internal_note = TextField(blank=True)

    date_joined = DateField(default=get_today)
    regional_center_support = ForeignKey(
        AdministrationUnit,
        related_name="supported_as_regional_center",
        on_delete=PROTECT,
        null=True,
        blank=True,
        limit_choices_to={"category__slug": "regional_center"},
    )
    basic_section_support = ForeignKey(
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

    def merge_with(self, other):
        assert other != self
        for field in self._meta.fields:
            if field.name in ["id", "subscribed_to_newsletter", "is_public", "user"]:
                continue

            elif field.name in [
                "regional_center_support",
                "basic_section_support",
                "has_recurrent_donation",
                "internal_note",
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
            if isinstance(relation, ManyToOneRel) or isinstance(relation, OneToOneRel):
                for obj in relation.field.model.objects.filter(
                    **{relation.field.name: other}
                ):
                    setattr(obj, relation.field.name, self)
                    obj.save()

            elif isinstance(relation, ManyToManyRel):
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


@translate_model
class VariableSymbol(Model):
    donor = ForeignKey(Donor, related_name="variable_symbols", on_delete=CASCADE)
    variable_symbol = PositiveBigIntegerField(unique=True)

    def __str__(self):
        return str(self.variable_symbol)

    class Meta:
        ordering = ("id",)


@translate_model
class Donation(Model):
    donor = ForeignKey(Donor, on_delete=PROTECT, related_name="donations", null=True)
    donated_at = DateField()
    amount = IntegerField()
    donation_source = ForeignKey(
        DonationSourceCategory, related_name="donations", on_delete=PROTECT
    )

    _variable_symbol = PositiveBigIntegerField(null=True)
    _import_id = PositiveIntegerField(null=True)
    info = TextField()

    def __str__(self):
        return f"{self.amount} Kč"

    class Meta:
        ordering = ("-donated_at",)

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
    file = FileField(upload_to="bank_records")

    def __str__(self):
        return "Nahrání bankovního záznamu"

    class Meta:
        ordering = ("id",)
