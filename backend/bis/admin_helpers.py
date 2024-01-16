from collections import OrderedDict
from urllib.parse import urlencode

from admin_auto_filters.filters import AutocompleteFilterFactory
from admin_numeric_filter.admin import RangeNumericFilter
from admin_numeric_filter.forms import SliderNumericForm
from django import forms
from django.contrib.admin import ListFilter, SimpleListFilter
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter


def get_admin_edit_url(obj):
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id]
    )
    return mark_safe(f'<a href="{url}">{obj}</a>')


def get_admin_list_url(klass, text, params=None):
    url = reverse(f"admin:{klass._meta.app_label}_{klass._meta.model_name}_changelist")
    if params:
        url += "?" + urlencode(params)
    return mark_safe(f'<a href="{url}">{text}</a>')


class YesNoFilter(SimpleListFilter):
    query = None

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
            self.used_parameters[self.parameter_name + "_from"] = value

        if self.parameter_name + "_to" in params:
            value = params.pop(self.parameter_name + "_to")
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
    annotate_fn = None
    cache_name = None
    single_date_only = False

    def __init__(self, field, request, params, model, model_admin, field_path):
        if self.custom_field_path:
            field_path = self.custom_field_path
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.custom_title:
            self.title = self.custom_title

    def queryset(self, request, queryset):
        if self.annotate_fn:
            queryset = queryset.annotate(**{self.custom_field_path: self.annotate_fn})

        return super(CustomDateRangeFilter, self).queryset(request, queryset)

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


def event_of_administration_unit_filter_factory(title, parameter_name, cache_name):
    class Filter(AutocompleteFilterFactory(title, parameter_name)):
        def queryset(self, request, queryset):
            datetime_query = getattr(request, cache_name, {})
            prefix = parameter_name.rsplit("__", 1)[0]

            for key, value in list(datetime_query.items()):
                datetime_query[key.replace(prefix + "__", "")] = value
                del datetime_query[key]

            if self.value() or datetime_query:
                items = self.rel_model.objects.all()
                if self.value():
                    if prefix == "memberships":
                        datetime_query["administration_unit"] = self.value()
                    else:
                        datetime_query["administration_units"] = self.value()

                items = items.filter(**datetime_query)

                if parameter_name == "memberships__administration_unit":
                    setattr(request, "membership_stats_query", datetime_query)

                queryset = queryset.filter(**{prefix + "__in": items}).distinct()
                return queryset.model.objects.filter(id__in=queryset.values_list("id"))
            else:
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


class CacheRangeNumericFilter(RangeNumericFilter):
    cache_name = None

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + "_from", None)
        if value_from is not None and value_from != "":
            filters.update(
                {
                    self.parameter_name
                    + "__gte": self.used_parameters.get(
                        self.parameter_name + "_from", None
                    ),
                }
            )

        value_to = self.used_parameters.get(self.parameter_name + "_to", None)
        if value_to is not None and value_to != "":
            filters.update(
                {
                    self.parameter_name
                    + "__lte": self.used_parameters.get(
                        self.parameter_name + "_to", None
                    ),
                }
            )

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
    query = None
    title = "Jen poslední členství"
    parameter_name = "only_latest_members"

    def lookups(self, request, model_admin):
        return (("no", "Zobrazit všechna členství"),)

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset

        if "created_at__year" in request.GET:
            queryset = queryset.filter(created_at__year=request.GET["created_at__year"])

        id_map = {}
        for membership_id, user_id in reversed(queryset.values_list("id", "user_id")):
            id_map[user_id] = membership_id

        return queryset.filter(id__in=id_map.values())

    def choices(self, changelist):
        res = list(super().choices(changelist))
        res[0]["display"] = "Zobraz pouze poslední členství od každého člena"
        return res
