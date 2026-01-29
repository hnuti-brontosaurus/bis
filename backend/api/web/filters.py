from django.core.validators import EMPTY_VALUES
from django.db.utils import ProgrammingError
from django_filters import (
    BaseInFilter,
    ChoiceFilter,
    DateFilter,
    FilterSet,
    NumberFilter,
    OrderingFilter,
)

from administration_units.models import AdministrationUnit
from categories.models import (
    AdministrationUnitCategory,
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
    EventTag,
    OpportunityCategory,
)
from event.models import Event
from opportunities.models import Opportunity
from regions.models import Region


class ChoiceInFilter(BaseInFilter, ChoiceFilter):
    pass


class BISOrderingFilter(OrderingFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        ordering = [self.get_ordering_value(param) for param in value] + ["id"]
        return qs.order_by(*ordering)


def get_choices(model, fn):
    try:
        return [fn(c) for c in model.objects.all()]
    except ProgrammingError:
        return []


class EventFilter(FilterSet):
    group = ChoiceInFilter(
        field_name="group__slug",
        choices=get_choices(EventGroupCategory, lambda x: (x.slug, x.name)),
    )
    category = ChoiceInFilter(
        field_name="category__slug",
        choices=get_choices(EventCategory, lambda x: (x.slug, x.name)),
    )
    tags = ChoiceInFilter(
        field_name="tags__slug",
        choices=get_choices(EventTag, lambda x: (x.slug, x.name)),
    )
    program = ChoiceInFilter(
        field_name="program__slug",
        choices=get_choices(EventProgramCategory, lambda x: (x.slug, x.name)),
    )
    intended_for = ChoiceInFilter(
        field_name="intended_for__slug",
        choices=get_choices(EventIntendedForCategory, lambda x: (x.slug, x.name)),
    )
    administration_unit = ChoiceInFilter(
        field_name="administration_units__id",
        choices=get_choices(AdministrationUnit, lambda x: (x.id, x.abbreviation)),
    )
    region = ChoiceInFilter(
        field_name="location__region__id",
        choices=get_choices(Region, lambda x: (x.id, x.name)),
    )
    duration = NumberFilter(field_name="duration")
    duration__lte = NumberFilter(field_name="duration", lookup_expr="gte")
    duration__gte = NumberFilter(field_name="duration", lookup_expr="lte")

    start__lte = DateFilter(field_name="start", lookup_expr="lte")
    start__gte = DateFilter(field_name="start", lookup_expr="gte")
    end__lte = DateFilter(field_name="end", lookup_expr="lte")
    end__gte = DateFilter(field_name="end", lookup_expr="gte")

    ordering = BISOrderingFilter(fields=["start", "end"])

    class Meta:
        model = Event
        fields = []


class OpportunityFilter(FilterSet):
    category = ChoiceInFilter(
        field_name="category__slug",
        choices=get_choices(OpportunityCategory, lambda x: (x.slug, x.name)),
    )

    class Meta:
        model = Opportunity
        fields = []


class AdministrationUnitFilter(FilterSet):
    category = ChoiceInFilter(
        field_name="category__slug",
        choices=get_choices(AdministrationUnitCategory, lambda x: (x.slug, x.name)),
    )

    class Meta:
        model = AdministrationUnit
        fields = []
