from bis.admin_helpers import (
    CacheRangeNumericFilter,
    CustomDateRangeFilter,
    ListAwareRangeNumericFilter,
    RawRangeNumericFilter,
    YesNoFilter,
    event_of_administration_unit_filter_factory,
)
from bis.models import Qualification
from bis.permissions import Permissions
from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.contrib.admin.filters import FieldListFilter
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.utils import get_fields_from_path
from django.core.exceptions import ValidationError
from django.db.models import Exists, Min, OuterRef, Q
from django.utils import timezone
from django.utils.timezone import now
from donations.models import (
    Donation,
    Donor,
    DonorEvent,
    Pledge,
    annotate_donation_stats,
)
from more_admin_filters import MultiSelectRelatedDropdownFilter


def sees_donors(viewer):
    return Permissions(viewer, Donor, "backend").has_view_permission()


def visible_donors(viewer):
    return Permissions(viewer, Donor, "backend").filter_queryset(Donor.objects.all())


def donation_source_ids(request):
    selected = request.GET.get("donations__donation_source__id__in", "")
    return [s for s in selected.split(",") if s]


def visible_donor_stats(request, model_admin):
    """The donors the viewer may see, with the stats the donor filters and
    the donor export work with, scoped to the chosen donation sources and the
    date range of the donation sum."""
    donors = visible_donors(request.user).annotate(
        has_active_recurrent_donation=Exists(
            Pledge.objects.filter(
                donor=OuterRef("pk"), is_recurrent=True, recurrent_state="collecting"
            )
        ),
        had_recurrent_donation=Exists(
            Pledge.objects.filter(
                donor=OuterRef("pk"), is_recurrent=True, recurrent_state="stopped"
            )
        ),
    )
    donation_filter = None
    if source_ids := donation_source_ids(request):
        donation_filter = Q(donations__donation_source_id__in=source_ids)
    sum_range_filter = DonationSumRangeFilter(
        Donation.donated_at.field,
        request,
        dict(request.GET.lists()),
        Donor,
        model_admin,
        "donations__donated_at",
    )
    return annotate_donation_stats(
        donors,
        donation_filter=donation_filter,
        sum_filter=sum_range_filter.narrow(request, donation_filter),
    )


def is_active(filter_spec, request):
    return any(request.GET.get(p) for p in filter_spec.expected_parameters())


def on_visible_donors(filter_class, donor_field_path=None):
    """A donor list filter for the user list. It filters the donors the viewer
    may see and keeps their users, so that it cannot tell anything about the
    gifts of a donor the viewer does not see.

    Pass the donor field path for a FieldListFilter and list the result as
    `("donor", ...)`, a path that does not make the changelist deduplicate."""
    if issubclass(filter_class, FieldListFilter):

        class Filter(filter_class):
            def __init__(self, field, request, params, model, model_admin, field_path):
                field = get_fields_from_path(Donor, donor_field_path)[-1]
                super().__init__(
                    field, request, params, Donor, model_admin, donor_field_path
                )
                self.model_admin = model_admin

    else:

        class Filter(filter_class):
            def __init__(self, request, params, model, model_admin):
                super().__init__(request, params, Donor, model_admin)
                self.model_admin = model_admin

    def queryset(self, request, users):
        if not is_active(self, request):
            return users
        donors = filter_class.queryset(
            self, request, visible_donor_stats(request, self.model_admin)
        )
        return users.filter(donor__in=donors.values("pk"))

    Filter.queryset = queryset
    return Filter


def on_visible_campaign_history(filter_class):
    """The campaign history hung on the donor before, so whoever does not see
    all users filters it only among the donors they see."""

    class Filter(filter_class):
        def has_output(self):
            # A related filter with a single choice hides itself, and the
            # changelist then applies its parameter as a plain lookup,
            # bypassing the restriction below.
            return True

        def queryset(self, request, users):
            users = super().queryset(request, users)
            if is_active(self, request) and not request.user.can_see_all:
                users = users.filter(donor__in=visible_donors(request.user))
            return users

    return Filter


class ColumnsFilter(admin.SimpleListFilter):
    title = "Sloupce"
    parameter_name = "columns"

    def lookups(self, request, model_admin):
        presets = [("organizer", "Organizátor")]
        if sees_donors(request.user):
            presets.append(("donor", "Dárce"))
        return presets

    def queryset(self, request, queryset):
        return queryset

    def choices(self, changelist):
        choices = super().choices(changelist)
        yield {**next(choices), "display": "Základní"}
        yield from choices


class HasDonorFilter(YesNoFilter):
    title = "Má přiřazeného dárce"
    parameter_name = "has_donor"
    query = {"donor__isnull": False}


class IsDonorFilter(admin.SimpleListFilter):
    title = "Má profil dárce"
    parameter_name = "is_donor"

    def lookups(self, request, model_admin):
        return (("yes", "Ano"), ("no", "Ne"))

    def queryset(self, request, users):
        donors = visible_donors(request.user)
        if self.value() == "yes":
            return users.filter(donor__in=donors)
        if self.value() == "no":
            return users.exclude(donor__in=donors)
        return users


class ActiveQualificationFilter(YesNoFilter):
    title = "Má aktivní kvalifikaci"
    parameter_name = "active_qualification"
    query = {"qualifications__valid_till__gte": timezone.now().date()}


class IsAdministrationUnitActiveFilter(YesNoFilter):
    title = "Je článek aktivní"
    parameter_name = "administration_unit_active"
    query = {"existed_till__isnull": True}


class AgeFilter(RawRangeNumericFilter):
    title = "Věk"
    parameter_name = "age"
    birthday_field = "birthday"

    def queryset(self, request, queryset):
        filters = {}

        def min_max_age(value):
            return max(0, min(200, int(value)))

        value_from = self.used_parameters.get(self.parameter_name + "_from")
        if value_from is not None and value_from != "":
            filters.update(
                {
                    f"{self.birthday_field}__lt": now().date()
                    - relativedelta(years=min_max_age(value_from))
                }
            )

        value_to = self.used_parameters.get(self.parameter_name + "_to")
        if value_to is not None and value_to != "":
            filters.update(
                {
                    f"{self.birthday_field}__gte": now().date()
                    - relativedelta(years=min_max_age(value_to) + 1)
                }
            )

        return queryset.filter(**filters)


class NoBirthdayFilter(YesNoFilter):
    title = "Datum narození vyplněno?"
    parameter_name = "birthday_set"
    query = {"birthday__isnull": False}


class NoLoginFilter(YesNoFilter):
    title = "Přihlásil se uživatel do BISu?"
    parameter_name = "login_set"
    query = {"last_login__isnull": False}


class FirstDonorsDonationFilter(CustomDateRangeFilter):
    custom_title = "Dle prvního daru"
    custom_field_path = "first_donation"


class LastDonorsDonationFilter(CustomDateRangeFilter):
    custom_title = "Dle posledního daru"
    custom_field_path = "last_donation"


class HasRecurrentDonationFilter(admin.SimpleListFilter):
    title = "Je pravidelný dárce"
    parameter_name = "has_recurrent_donation_filter"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Ano"),
            ("no", "Ne"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(has_active_recurrent_donation=True)
        if self.value() == "no":
            return queryset.filter(has_active_recurrent_donation=False)


class IsCompanyDonorFilter(YesNoFilter):
    title = "Firemní dárce"
    parameter_name = "is_company_donor"
    query = {"company__isnull": False}


class RecurringDonorWhoStoppedFilter(admin.SimpleListFilter):
    title = "Pravidelný dárce bez daru za poslední 2 měsíce"
    parameter_name = "reccuring_donor_who_stopped"

    def lookups(self, request, model_admin):
        return (("yes", "Jen"),)

    def queryset(self, request, queryset):
        if self.value() == "yes":
            queryset = queryset.exclude(
                donations__donated_at__gte=now() - relativedelta(months=2)
            ).filter(had_recurrent_donation=True, has_active_recurrent_donation=False)
        return queryset


class DonationSumRangeFilter(CustomDateRangeFilter):
    custom_field_path = "donated_at"
    custom_title = "Suma darů z rozmezí"

    def narrow(self, request, annotate_filter):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                query = self._make_query_filter(request, validated_data)

                for key, value in query.items():
                    q = Q(**{f"donations__{key}": value})
                    if annotate_filter:
                        annotate_filter &= q
                    else:
                        annotate_filter = q

        return annotate_filter

    def queryset(self, request, queryset):
        return queryset


class DonationSumAmountFilter(ListAwareRangeNumericFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        field_path = "donations_sum"
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = "Dle sumy darů"


class MainOrganizerOfEventRangeFilter(CustomDateRangeFilter):
    custom_title = "Dle: Hlavní organizátor v období"
    cache_name = "main_organizer_of_event_range_query_cache"


class EventsWhereWasAsMainOrganizerCountFilter(CacheRangeNumericFilter):
    cache_name = "main_organizer_of_event_count_query_cache"
    custom_title = "Dle: Hlavní organizátor počtu akcí"


class OrganizerOfEventRangeFilter(CustomDateRangeFilter):
    custom_title = "Dle: Organizátor v období"
    cache_name = "organizer_of_event_range_query_cache"


class EventsWhereWasOrganizerCountFilter(CacheRangeNumericFilter):
    cache_name = "organizer_of_event_count_query_cache"
    custom_title = "Dle: Organizátor počtu akcí"


class ParticipatedInEventRangeFilter(CustomDateRangeFilter):
    custom_title = "Dle: Účast na akci v období"
    cache_name = "participated_in_event_range_query_cache"


class ParticipatedInEventsCountFilter(CacheRangeNumericFilter):
    cache_name = "participated_in_event_count_query_cache"
    custom_title = "Dle: Účastník počtu akcí"


class FirstParticipatedInEventRangeFilter(CustomDateRangeFilter):
    custom_title = "Dle: První účast na akci v období"
    annotate_fn = Min("participated_in_events__event__start")
    custom_field_path = "first_participated_in_event"


MainOrganizerOfEventOfAdministrationUnitFilter = (
    event_of_administration_unit_filter_factory(
        "Hlavní organizátor vybrané OJ",
        "events_where_was_as_main_organizer__administration_units",
        MainOrganizerOfEventRangeFilter.cache_name,
        EventsWhereWasAsMainOrganizerCountFilter.cache_name,
    )
)
OrganizerOfEventOfAdministrationUnitFilter = (
    event_of_administration_unit_filter_factory(
        "Organizátor vybrané OJ",
        "events_where_was_organizer__administration_units",
        OrganizerOfEventRangeFilter.cache_name,
        EventsWhereWasOrganizerCountFilter.cache_name,
    )
)
ParticipatedInEventOfAdministrationUnitFilter = (
    event_of_administration_unit_filter_factory(
        "Účast na akci vybrané OJ",
        "participated_in_events__event__administration_units",
        ParticipatedInEventRangeFilter.cache_name,
        ParticipatedInEventsCountFilter.cache_name,
    )
)


class MemberDuringYearsFilter(CacheRangeNumericFilter):
    cache_name = "memberships_years_query_cache"


class MembershipCountFilter(CacheRangeNumericFilter):
    cache_name = "memberships_count_query_cache"
    custom_title = "Počet členství"


MemberOfAdministrationUnitFilter = event_of_administration_unit_filter_factory(
    "Členství ve organizační jednotce",
    "memberships__administration_unit",
    MemberDuringYearsFilter.cache_name,
    MembershipCountFilter.cache_name,
)


class QualificationValidAtFilter(CustomDateRangeFilter):
    custom_title = "Platná v den"
    cache_name = "qualification_valid_at_query_cache"
    single_date_only = True


class QualificationCategoryFilter(MultiSelectRelatedDropdownFilter):
    def queryset(self, request, queryset):
        date_filter = getattr(request, QualificationValidAtFilter.cache_name, {})
        if date_filter:
            value = date_filter["qualifications__valid_since"]
            del date_filter["qualifications__valid_since"]
            date_filter["valid_since__lte"] = value
            date_filter["valid_till__gte"] = value

        params = Q()
        for lookup_arg, value in self.used_parameters.items():
            lookup_arg = lookup_arg.replace("qualifications__", "")
            query = {lookup_arg: value}
            query.update(date_filter)
            params |= Q(**query)

        if not params and date_filter:
            params = Q(**date_filter)

        if params:
            try:
                return queryset.model.objects.filter(
                    pk__in=queryset.filter(
                        qualifications__in=Qualification.objects.filter(params)
                    ).values_list("pk")
                )
            except (ValueError, ValidationError) as e:
                # Fields may raise a ValueError or ValidationError when converting
                # the parameters to the correct type.
                raise IncorrectLookupParameters(e)

        return queryset


class EventStatsDateFilter(CustomDateRangeFilter):
    custom_title = "Datum pro statistiku věku účastníků a orgů"
    single_date_only = True
    cache_name = "events_stats_date_cache"


class UserStatsDateFilter(CustomDateRangeFilter):
    custom_title = "Datum pro statistiku věku"
    single_date_only = True
    cache_name = "users_stats_date_cache"


class HasFeedbackFilter(YesNoFilter):
    title = "Má ZV"
    parameter_name = "has_feedback"
    query = {"feedbacks__isnull": False}


CAMPAIGN_EVENTS_PATH = "campaign_events__"


def campaign_filter_ids(request):
    """Campaigns picked in the user list's campaign filter."""
    selected = request.GET.get(f"{CAMPAIGN_EVENTS_PATH}campaign__id__in", "")
    return [c for c in selected.split(",") if c]


class HasPledgeInCampaignFilter(admin.SimpleListFilter):
    title = "Příslib vyplněn"
    parameter_name = "has_pledge_in_campaign"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Ano"),
            ("no", "Ne"),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        campaign_ids = campaign_filter_ids(request)

        q = Q(pledge__gt="")
        if campaign_ids:
            q &= Q(campaign_id__in=campaign_ids)

        users_with_pledge = DonorEvent.objects.filter(q).values("user_id")

        if self.value() == "yes":
            return queryset.filter(pk__in=users_with_pledge)
        if self.value() == "no":
            return queryset.exclude(pk__in=users_with_pledge)

        return queryset


class MultiSelectRelatedDropdownAndCampaignFilter(MultiSelectRelatedDropdownFilter):
    """Like MultiSelectRelatedDropdownFilter, but ANDs with the campaign filter when campaigns are selected."""

    def queryset(self, request, queryset):
        if not self.used_parameters:
            return queryset

        campaign_ids = campaign_filter_ids(request)
        if not campaign_ids:
            return super().queryset(request, queryset)

        donor_event_q = Q(campaign_id__in=campaign_ids)
        for lookup_arg, value in self.used_parameters.items():
            donor_event_q &= Q(
                **{lookup_arg.replace(CAMPAIGN_EVENTS_PATH, "", 1): value}
            )

        try:
            return queryset.filter(
                pk__in=DonorEvent.objects.filter(donor_event_q).values("user_id")
            )
        except (ValueError, ValidationError) as e:
            raise IncorrectLookupParameters(e)
