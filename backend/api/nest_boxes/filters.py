from categories.models import NestBoxType
from django.contrib.gis.geos import Polygon
from django_filters import rest_framework as filters
from nest_boxes.models import Batch, Check, NestBox, SeasonState
from rest_framework.exceptions import ValidationError


class SeasonStateFilter(filters.FilterSet):
    """Over `NestBox.objects.with_season_state()`; the map of areas filters by these."""

    type = filters.ModelMultipleChoiceFilter(queryset=NestBoxType.objects.all())
    season_state = filters.MultipleChoiceFilter(choices=SeasonState.choices)
    administration_unit = filters.NumberFilter(field_name="area__administration_unit")

    class Meta:
        model = NestBox
        fields = ("region", "is_verified")


class NestBoxFilter(SeasonStateFilter):
    status = filters.MultipleChoiceFilter(choices=NestBox.Status.choices)
    # west,south,east,north in degrees, as maplibre's getBounds().toArray().flat()
    bbox = filters.CharFilter(method="filter_bbox")
    batch = filters.NumberFilter(field_name="batches")
    last_checked_before = filters.DateFilter(
        field_name="last_checked_on", lookup_expr="lt"
    )
    last_checked_after = filters.DateFilter(
        field_name="last_checked_on", lookup_expr="gte"
    )
    never_checked = filters.BooleanFilter(
        field_name="last_checked_on", lookup_expr="isnull"
    )
    # The boxes ticked in a list, for an export of just those
    id = filters.BaseInFilter()

    class Meta:
        model = NestBox
        fields = ("area", "region", "is_verified", "is_confirmed", "condition")

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
