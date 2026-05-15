import django_filters
from bis.models import Location, User
from event.models import Event


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class UUIDInFilter(django_filters.BaseInFilter, django_filters.UUIDFilter):
    pass


class UserFilter(django_filters.FilterSet):
    id = UUIDInFilter()
    _search_id = UUIDInFilter()

    class Meta:
        model = User
        fields = []


class EventFilter(django_filters.FilterSet):
    id = NumberInFilter()
    is_archived = django_filters.BooleanFilter()
    is_closed = django_filters.BooleanFilter()
    is_canceled = django_filters.BooleanFilter()

    class Meta:
        model = Event
        fields = []


class LocationFilter(django_filters.FilterSet):
    id = NumberInFilter()

    class Meta:
        model = Location
        fields = []
