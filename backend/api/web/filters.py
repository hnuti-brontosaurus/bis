from django.db.utils import ProgrammingError
from django_filters import *

from administration_units.models import AdministrationUnit
from categories.models import EventCategory, EventProgramCategory, EventIntendedForCategory, OpportunityCategory, \
    AdministrationUnitCategory, EventGroupCategory
from event.models import Event
from opportunities.models import Opportunity


class ChoiceInFilter(BaseInFilter, ChoiceFilter):
    pass


def get_choices(model, fn):
    try:
        return [fn(c) for c in model.objects.all()]
    except ProgrammingError:
        return []


class EventFilter(FilterSet):
    group = ChoiceInFilter(
        field_name='group__slug',
        choices=get_choices(EventGroupCategory, lambda x: (x.slug, x.name))
    )
    category = ChoiceInFilter(
        field_name='category__slug',
        choices=get_choices(EventCategory, lambda x: (x.slug, x.name))
    )
    program = ChoiceInFilter(
        field_name='program__slug',
        choices=get_choices(EventProgramCategory, lambda x: (x.slug, x.name))
    )
    intended_for = ChoiceInFilter(
        field_name='intended_for__slug',
        choices=get_choices(EventIntendedForCategory, lambda x: (x.slug, x.name))
    )
    administration_unit = ChoiceInFilter(
        field_name='administration_units__id',
        choices=get_choices(AdministrationUnit, lambda x: (x.id, x.abbreviation))
    )
    duration = NumberFilter(field_name='duration')
    duration__lte = NumberFilter(field_name='duration', lookup_expr='gte')
    duration__gte = NumberFilter(field_name='duration', lookup_expr='lte')

    start__lte = DateFilter(field_name='start', lookup_expr='lte')
    start__gte = DateFilter(field_name='start', lookup_expr='gte')
    end__lte = DateFilter(field_name='end', lookup_expr='lte')
    end__gte = DateFilter(field_name='end', lookup_expr='gte')

    ordering = OrderingFilter(fields=['start', 'end'])

    class Meta:
        model = Event
        fields = []

    # todo set choices at __init__, so addming au does not require restart


class OpportunityFilter(FilterSet):
    category = ChoiceInFilter(
        field_name='category__slug',
        choices=get_choices(OpportunityCategory, lambda x: (x.slug, x.name))
    )

    class Meta:
        model = Opportunity
        fields = []


class AdministrationUnitFilter(FilterSet):
    category = ChoiceInFilter(
        field_name='category__slug',
        choices=get_choices(AdministrationUnitCategory, lambda x: (x.slug, x.name))
    )

    class Meta:
        model = AdministrationUnit
        fields = []
