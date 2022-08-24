from admin_numeric_filter.admin import RangeNumericFilter
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import ValidationError
from django.db.models import Min, Max, OuterRef, Sum, Subquery, Q
from django.utils import timezone
from django.utils.timezone import now
from more_admin_filters import MultiSelectRelatedDropdownFilter

from bis.admin_helpers import YesNoFilter, RawRangeNumericFilter, CustomDateRangeFilter, \
    event_of_administration_unit_filter_factory, CacheRangeNumericFilter
from bis.models import Qualification


class HasDonorFilter(YesNoFilter):
    title = 'Má přiřazeného dárce'
    parameter_name = 'has_donor'
    query = {'donor__isnull': False}


class ActiveQualificationFilter(YesNoFilter):
    title = 'Má aktivní kvalifikaci'
    parameter_name = 'active_qualification'
    query = {'qualifications__valid_till__gte': timezone.now().date()}


class IsAdministrationUnitActiveFilter(YesNoFilter):
    title = 'Je článek aktivní'
    parameter_name = 'administration_unit_active'
    query = {'existed_till__isnull': True}


class AgeFilter(RawRangeNumericFilter):
    title = 'Věk'
    parameter_name = 'age'

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + '_from', None)
        if value_from is not None and value_from != '':
            filters.update({'birthday__lt': now().date() - relativedelta(years=int(value_from))})

        value_to = self.used_parameters.get(self.parameter_name + '_to', None)
        if value_to is not None and value_to != '':
            filters.update({'birthday__gte': now().date() - relativedelta(years=int(value_to) + 1)})

        return queryset.filter(**filters)


class NoBirthdayFilter(YesNoFilter):
    title = 'Datum narození vyplněno?'
    parameter_name = 'birthday_set'
    query = {'birthday__isnull': False}


class FirstDonorsDonationFilter(CustomDateRangeFilter):
    custom_title = 'Dle prvního daru'
    custom_field_path = 'first_donation'
    annotate_fn = Min('donations__donated_at')


class LastDonorsDonationFilter(CustomDateRangeFilter):
    custom_title = 'Dle posledního daru'
    custom_field_path = 'last_donation'
    annotate_fn = Max('donations__donated_at')


class RecurringDonorWhoStoppedFilter(admin.SimpleListFilter):
    title = 'Pravidelný dárce bez daru za poslední 2 měsíce'
    parameter_name = 'reccuring_donor_who_stopped'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Jen'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            queryset = queryset.exclude(donations__donated_at__gte=now() - relativedelta(months=2)) \
                .filter(has_recurrent_donation=True)
        return queryset


class DonationSumRangeFilter(CustomDateRangeFilter):
    custom_field_path = 'donated_at'
    custom_title = 'Suma darů z rozmezí'

    def queryset(self, request, queryset):
        annotate_with = Sum('donations__amount')

        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                query = self._make_query_filter(request, validated_data)
                query['donor'] = OuterRef('pk')
                donations = apps.get_model('donations', 'Donation').objects.filter(**query).values('donor')
                donations_sum = donations.annotate(total=Sum('amount')).values('total')
                annotate_with = Subquery(donations_sum)

        queryset = queryset.annotate(donations_sum=annotate_with)
        return queryset


class DonationSumAmountFilter(RangeNumericFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        field_path = 'donations_sum'
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = 'Dle sumy darů'


class MainOrganizerOfEventRangeFilter(CustomDateRangeFilter):
    custom_title = 'Dle: Hlavní org akce v rozmezí'
    cache_name = 'main_organizer_of_event_range_query_cache'


class OrganizerOfEventRangeFilter(CustomDateRangeFilter):
    custom_title = 'Dle: Org akce v rozmezí'
    cache_name = 'organizer_of_event_range_query_cache'


class ParticipatedInEventRangeFilter(CustomDateRangeFilter):
    custom_title = 'Dle: Účast na akci v rozmezí'
    cache_name = 'participated_in_event_range_query_cache'


MainOrganizerOfEventOfAdministrationUnitFilter = event_of_administration_unit_filter_factory(
    'Hlavní org akcí vybraného článku',
    'events_where_was_as_main_organizer__administration_units',
    MainOrganizerOfEventRangeFilter.cache_name
)
OrganizerOfEventOfAdministrationUnitFilter = event_of_administration_unit_filter_factory(
    'Org akcí vybraného článku',
    'events_where_was_organizer__administration_units',
    OrganizerOfEventRangeFilter.cache_name
)
ParticipatedInEventOfAdministrationUnitFilter = event_of_administration_unit_filter_factory(
    'Účast na akci vybraného článku',
    'participated_in_events__event__administration_units',
    ParticipatedInEventRangeFilter.cache_name
)


class MemberDuringYearsFilter(CacheRangeNumericFilter):
    cache_name = 'memberships_years_query_cache'


MemberOfAdministrationUnitFilter = event_of_administration_unit_filter_factory(
    'Dle: Členství ve článku',
    'memberships__administration_unit',
    MemberDuringYearsFilter.cache_name
)


class QualificationValidAtFilter(CustomDateRangeFilter):
    custom_title = 'Platná v den'
    cache_name = 'qualification_valid_at_query_cache'
    single_date_only = True


class QualificationCategoryFilter(MultiSelectRelatedDropdownFilter):
    def queryset(self, request, queryset):
        date_filter = getattr(request, QualificationValidAtFilter.cache_name, {})
        if date_filter:
            value = date_filter['qualifications__valid_since']
            del date_filter['qualifications__valid_since']
            date_filter['valid_since__lte'] = value
            date_filter['valid_till__gte'] = value

        params = Q()

        for lookup_arg, value in self.used_parameters.items():
            lookup_arg = lookup_arg.replace('qualifications__', '')
            query = {lookup_arg: value}
            query.update(date_filter)
            params |= Q(**query)
        try:
            return queryset.filter(qualifications__in=Qualification.objects.filter(params))
        except (ValueError, ValidationError) as e:
            # Fields may raise a ValueError or ValidationError when converting
            # the parameters to the correct type.
            raise IncorrectLookupParameters(e)
