from collections import OrderedDict
from urllib.parse import urlencode

from admin_auto_filters.filters import AutocompleteFilterFactory
from admin_numeric_filter.admin import RangeNumericFilter
from admin_numeric_filter.forms import SliderNumericForm
from django import forms
from django.contrib.admin import ListFilter, SimpleListFilter
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.gis.geos import Point
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter


def _unwrap_list_parameters(filter_instance):
    for key, value in filter_instance.used_parameters.items():
        if isinstance(value, list):
            filter_instance.used_parameters[key] = value[0] if value else None


def _unwrap_list_params(params):
    for key, value in params.items():
        if isinstance(value, list):
            params[key] = value[0] if value else ""


def get_admin_edit_url(obj):
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id]
    )
    return mark_safe(f'<a href="{url}">{obj}</a>')


def get_admin_list_url(klass, text, params=None, title=""):
    url = reverse(f"admin:{klass._meta.app_label}_{klass._meta.model_name}_changelist")
    if params:
        url += "?" + urlencode(params)
    return mark_safe(f'<a href="{url}" title="{title}">{text}</a>')


class YesNoFilter(SimpleListFilter):
    query = None
    distinct = False

    def lookups(self, request, model_admin):
        return (
            ("yes", "Ano"),
            ("no", "Ne"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            queryset = queryset.filter(**self.query)
        if self.value() == "no":
            queryset = queryset.exclude(**self.query)
        if self.distinct:
            queryset = queryset.distinct()
        return queryset


class RawRangeNumericFilter(ListFilter):
    parameter_name = None
    # min_value = 0
    # max_value = 100
    template = "admin/filter_numeric_range.html"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.request = request

        if self.parameter_name + "_from" in params:
            value = params.pop(self.parameter_name + "_from")
            if isinstance(value, list):
                value = value[0] if value else None
            self.used_parameters[self.parameter_name + "_from"] = value

        if self.parameter_name + "_to" in params:
            value = params.pop(self.parameter_name + "_to")
            if isinstance(value, list):
                value = value[0] if value else None
            self.used_parameters[self.parameter_name + "_to"] = value

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + "_from", None)
        if value_from is not None and value_from != "":
            filters.update({self.parameter_name + "__gte": value_from})

        value_to = self.used_parameters.get(self.parameter_name + "_to", None)
        if value_to is not None and value_to != "":
            filters.update({self.parameter_name + "__lte": value_to})

        return queryset.filter(**filters)

    def expected_parameters(self):
        return [
            "{}_from".format(self.parameter_name),
            "{}_to".format(self.parameter_name),
        ]

    def has_output(self):
        return True

    def choices(self, changelist):
        return (
            {
                "decimals": 0,
                "step": 1,
                "parameter_name": self.parameter_name,
                "request": self.request,
                # 'min': self.min_value,
                # 'max': self.max_value,
                # 'value_from': self.used_parameters.get(self.parameter_name + '_from'),
                # 'value_to': self.used_parameters.get(self.parameter_name + '_to'),
                "form": SliderNumericForm(
                    name=self.parameter_name,
                    data={
                        self.parameter_name
                        + "_from": self.used_parameters.get(
                            self.parameter_name + "_from"
                        ),
                        self.parameter_name
                        + "_to": self.used_parameters.get(self.parameter_name + "_to"),
                    },
                ),
            },
        )


class CustomDateRangeFilter(DateRangeFilter):
    custom_field_path = None
    custom_title = None
    cache_name = None
    single_date_only = False

    def __init__(self, field, request, params, model, model_admin, field_path):
        if self.custom_field_path:
            field_path = self.custom_field_path
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.custom_title:
            self.title = self.custom_title

    def _make_query_filter(self, request, validated_data):
        query_filter = super()._make_query_filter(request, validated_data)
        if self.single_date_only:
            for key, value in list(query_filter.items()):
                query_filter[key.replace("__gte", "")] = value
                del query_filter[key]

        if self.cache_name:
            setattr(request, self.cache_name, query_filter)
            return {}

        return query_filter

    def _get_expected_fields(self):
        if self.single_date_only:
            return [self.lookup_kwarg_gte]
        return super(CustomDateRangeFilter, self)._get_expected_fields()

    def _get_form_fields(self):
        if self.single_date_only:
            return OrderedDict(
                (
                    (
                        self.lookup_kwarg_gte,
                        forms.DateField(
                            label="",
                            widget=AdminDateWidget(attrs={"placeholder": "Datum"}),
                            localize=True,
                            required=False,
                        ),
                    ),
                )
            )
        return super(CustomDateRangeFilter, self)._get_form_fields()


def event_of_administration_unit_filter_factory(
    title, parameter_name, date_cache_name, count_cache_name
):
    class Filter(AutocompleteFilterFactory(title, parameter_name)):
        def queryset(self, request, queryset):
            datetime_query = getattr(request, date_cache_name, {})
            prefix = parameter_name.rsplit("__", 1)[0]

            annotate_name = f"{prefix}_count"
            count_query = getattr(request, count_cache_name, {})
            for key, value in list(count_query.items()):
                count_query[annotate_name + "__" + key.split("__")[-1]] = value
                del count_query[key]

            if self.value() or datetime_query or count_query:
                if self.value():
                    if prefix == "memberships":
                        datetime_query[f"{prefix}__administration_unit"] = self.value()
                    else:
                        datetime_query[f"{prefix}__administration_units"] = self.value()

                annotation = {annotate_name: Count(prefix, filter=Q(**datetime_query))}
                queryset = queryset.annotate(**annotation)

                if not count_query:
                    count_query = {annotate_name + "__gte": 1}

                for key, value in list(datetime_query.items()):
                    datetime_query[key.replace(prefix + "__", "")] = value
                    del datetime_query[key]
                if parameter_name == "memberships__administration_unit":
                    setattr(request, "membership_stats_query", datetime_query)

                queryset = queryset.filter(**count_query)
                return queryset.model.objects.filter(id__in=queryset.values_list("id"))

            return queryset

    return Filter


class TextOnlyFilter(ListFilter):
    def has_output(self):
        return True

    def queryset(self, request, queryset):
        return queryset

    def choices(self, changelist):
        return []

    def expected_parameters(self):
        return None


def list_filter_extra_title(custom_title):
    class Filter(TextOnlyFilter):
        template = "admin/title_filter.html"
        title = custom_title

    return Filter


def list_filter_extra_text(custom_title):
    class Filter(TextOnlyFilter):
        template = "admin/text_filter.html"
        title = custom_title

    return Filter


def list_filter_extra_note(custom_title):
    class Filter(TextOnlyFilter):
        template = "admin/note_filter.html"
        title = custom_title

    return Filter


class UserExportFilter(TextOnlyFilter):
    template = "admin/user_export_filter.html"
    title = "Export dle e-mailů"


class CacheRangeNumericFilter(RangeNumericFilter):
    cache_name = None
    custom_title = None

    def __init__(self, field, request, params, model, model_admin, field_path):
        _unwrap_list_params(params)
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.custom_title:
            self.title = self.custom_title

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + "_from", None)
        if value_from is not None and value_from != "":
            filters[self.parameter_name + "__gte"] = value_from

        value_to = self.used_parameters.get(self.parameter_name + "_to", None)
        if value_to is not None and value_to != "":
            filters[self.parameter_name + "__lte"] = value_to

        setattr(request, self.cache_name, filters)
        return queryset


class LatLongWidget(forms.TextInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs["placeholder"] = "49.20091N, 16.62262E"
        super().__init__(attrs)

    def format_value(self, value):
        if isinstance(value, Point):
            coords = value.coords[::-1]
            return f"{coords[0]}N, {coords[1]}E"
        return value

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if not value:
            return value

        try:
            coords = [c.strip() for c in value.split(",")]
            assert coords[0][-1] == "N" and coords[1][-1] == "E"
            return Point(float(coords[1][:-1]), float(coords[0][:-1]))
        except (IndexError, AssertionError, ValueError):
            pass

        return value


class LatestMembershipOnlyFilter(SimpleListFilter):
    title = "Jen poslední členství"
    parameter_name = "only_latest_members"

    def lookups(self, request, model_admin):
        return (("no", "Zobrazit všechna členství"),)

    def queryset(self, request, queryset):
        setattr(request, "only_latest_members_filter", self.value())
        return queryset

    def choices(self, changelist):
        res = list(super().choices(changelist))
        res[0]["display"] = "Zobraz pouze poslední členství od každého člena"
        return res


class MembershipYearFilter(RangeNumericFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        _unwrap_list_params(params)
        super().__init__(field, request, params, model, model_admin, field_path)

    def queryset(self, request, queryset):
        queryset = super().queryset(request, queryset)

        if getattr(request, "only_latest_members_filter", "no") == "no":
            return queryset

        if "_year__year" in request.GET:
            queryset = queryset.filter(_year__year=request.GET["_year__year"])

        id_map = {}
        for membership_id, user_id in reversed(queryset.values_list("id", "user_id")):
            id_map[user_id] = membership_id

        return queryset.filter(id__in=id_map.values())
