from categories.models import NestBoxType
from django.contrib.gis.geos import Polygon
from django.db.models import Exists, OuterRef, Q
from django_filters import rest_framework as filters
from nest_boxes.models import (
    ATTENTION_STATUSES,
    Batch,
    Check,
    NestBox,
    SeasonState,
)
from rest_framework.exceptions import ValidationError

MOVED = "moved"


class SeasonStateFilter(filters.FilterSet):
    """Over `NestBox.objects.with_season_state()`; the map of areas filters by these."""

    type = filters.ModelMultipleChoiceFilter(queryset=NestBoxType.objects.all())
    season_state = filters.MultipleChoiceFilter(choices=SeasonState.choices)
    administration_unit = filters.NumberFilter(field_name="area__administration_unit")
    # An annotation, see NestBoxQuerySet.with_is_verified
    is_verified = filters.BooleanFilter()
    # Why a box needs attention: a status of ATTENTION_STATUSES, or "moved"
    problem = filters.MultipleChoiceFilter(
        choices=[
            *((status, status.label) for status in ATTENTION_STATUSES),
            (MOVED, "přemístit"),
        ],
        method="filter_problem",
    )
    # By the last confirmed check, as Exists: season_states can't group an
    # aggregate like box_queryset's last_checked_on
    last_checked_before = filters.DateFilter(method="filter_last_checked_before")
    last_checked_after = filters.DateFilter(method="filter_last_checked_after")
    never_checked = filters.BooleanFilter(method="filter_never_checked")

    class Meta:
        model = NestBox
        fields = ("region",)

    def filter_problem(self, queryset, name, value):
        shown = Q(status__in=[item for item in value if item != MOVED])
        if MOVED in value:
            shown |= Q(should_be_moved=True)
        return queryset.filter(shown)

    @staticmethod
    def confirmed_check(**conditions):
        return Exists(
            Check.objects.filter(box=OuterRef("pk"), is_confirmed=True, **conditions)
        )

    def filter_last_checked_before(self, queryset, name, value):
        return queryset.filter(
            self.confirmed_check(), ~self.confirmed_check(date__gte=value)
        )

    def filter_last_checked_after(self, queryset, name, value):
        return queryset.filter(self.confirmed_check(date__gte=value))

    def filter_never_checked(self, queryset, name, value):
        checked = self.confirmed_check()
        return queryset.filter(~checked if value else checked)


class NestBoxFilter(SeasonStateFilter):
    status = filters.MultipleChoiceFilter(choices=NestBox.Status.choices)
    # The map legend's entries: a season state, or "ended", which has none
    state = filters.MultipleChoiceFilter(
        choices=[*SeasonState.choices, (NestBox.Status.ENDED, "ended")],
        method="filter_state",
    )
    # west,south,east,north in degrees, as maplibre's getBounds().toArray().flat()
    bbox = filters.CharFilter(method="filter_bbox")
    batch = filters.NumberFilter(field_name="batches")
    # The boxes ticked in a list, for an export of just those
    id = filters.BaseInFilter()

    class Meta:
        model = NestBox
        fields = ("area", "region")

    def filter_state(self, queryset, name, value):
        shown = Q(season_state__in=value)
        if NestBox.Status.ENDED in value:
            shown |= Q(status=NestBox.Status.ENDED)
        return queryset.filter(shown)

    def filter_bbox(self, queryset, name, value):
        try:
            bounds = [float(number) for number in value.split(",")]
            polygon = Polygon.from_bbox(bounds)
        except ValueError:
            raise ValidationError({"bbox": "Očekávají se čtyři čísla."})
        polygon.srid = 4326
        return queryset.filter(location__within=polygon)


class CheckFilter(filters.FilterSet):
    area = filters.NumberFilter(field_name="box__area")

    class Meta:
        model = Check
        fields = ("box", "batch", "season", "is_confirmed")


class BatchFilter(filters.FilterSet):
    is_open = filters.BooleanFilter(field_name="closed_at", lookup_expr="isnull")

    class Meta:
        model = Batch
        fields = ("area",)
