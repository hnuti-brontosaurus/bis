from categories.models import NestBoxType
from django_filters import rest_framework as filters
from nest_boxes.models import Batch, Check, NestBox


class NestBoxFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(choices=NestBox.Status.choices)
    type = filters.ModelMultipleChoiceFilter(queryset=NestBoxType.objects.all())
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
        fields = ("area", "is_verified", "is_confirmed", "condition")


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
