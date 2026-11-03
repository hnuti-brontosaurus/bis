from admin_auto_filters.filters import AutocompleteFilterFactory
from admin_numeric_filter.admin import NumericFilterModelAdmin
from bis.admin_filters import (
    AgeFilter,
    ColumnsFilter,
    DonationSumAmountFilter,
    DonationSumRangeFilter,
    EventsWhereWasAsMainOrganizerCountFilter,
    EventsWhereWasOrganizerCountFilter,
    FirstDonorsDonationFilter,
    FirstParticipatedInEventRangeFilter,
    HasPledgeInCampaignFilter,
    HasRecurrentDonationFilter,
    IsCompanyDonorFilter,
    IsDonorFilter,
    LastDonorsDonationFilter,
    MainOrganizerOfEventOfAdministrationUnitFilter,
    MainOrganizerOfEventRangeFilter,
    MemberDuringYearsFilter,
    MemberOfAdministrationUnitFilter,
    MembershipCountFilter,
    MultiSelectRelatedDropdownAndCampaignFilter,
    NoBirthdayFilter,
    NoLoginFilter,
    OrganizerOfEventOfAdministrationUnitFilter,
    OrganizerOfEventRangeFilter,
    ParticipatedInEventOfAdministrationUnitFilter,
    ParticipatedInEventRangeFilter,
    ParticipatedInEventsCountFilter,
    QualificationCategoryFilter,
    QualificationValidAtFilter,
    RecurringDonorWhoStoppedFilter,
    UserStatsDateFilter,
    on_visible_campaign_history,
    on_visible_donors,
    sees_donors,
    visible_donor_stats,
    visible_donors,
)
from bis.admin_helpers import (
    LatestMembershipOnlyFilter,
    LatLongWidget,
    MembershipYearFilter,
    NullsLast,
    QuerySearchMixin,
    UserExportFilter,
    get_admin_edit_url,
    list_filter_extra_note,
    list_filter_extra_text,
    list_filter_extra_title,
)
from bis.admin_permissions import PermissionMixin
from bis.emails import donation_confirmation
from bis.helpers import make_a, make_table
from bis.models import (
    EYCACard,
    Location,
    LocationContactPerson,
    LocationPatron,
    LocationPhoto,
    Membership,
    Qualification,
    QualificationNote,
    User,
    UserAddress,
    UserClosePerson,
    UserContactAddress,
    UserEmail,
)
from bis.permissions import Permissions
from categories.models import (
    DonorEventCategory,
    MembershipCategory,
    PronounCategory,
    QualificationCategory,
)
from dateutil.utils import today
from django import forms
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, action, helpers
from django.contrib.admin.filters import BooleanFieldListFilter
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth.models import Group
from django.contrib.gis.db.models import PointField
from django.contrib.messages import ERROR
from django.core.exceptions import ValidationError
from django.db.models import (
    Exists,
    Max,
    OuterRef,
    Subquery,
    Sum,
    prefetch_related_objects,
)
from django.db.models.functions import Coalesce
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from donations.models import (
    Company,
    Donation,
    Donor,
    DonorEvent,
    FundraisingCampaign,
    Pledge,
    VariableSymbol,
)
from login_code.models import guess_birthday_throttle
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import (
    NestedModelAdmin,
    NestedModelAdminMixin,
    NestedStackedInline,
    NestedTabularInline,
)
from opportunities.models import OfferedHelp
from other.models import DuplicateUser, UserTag
from rangefilter.filters import DateRangeFilter
from rest_framework.authtoken.models import TokenProxy
from rest_framework.exceptions import Throttled
from translation.translate import _
from xlsx_export.export import export_to_xlsx, get_donation_confirmation

admin.site.unregister(TokenProxy)
admin.site.unregister(Group)


class LocationPhotosAdmin(PermissionMixin, NestedTabularInline):
    model = LocationPhoto
    readonly_fields = ("photo_tag",)


class LocationContactPersonAdmin(PermissionMixin, NestedTabularInline):
    model = LocationContactPerson


class LocationPatronAdmin(PermissionMixin, NestedTabularInline):
    model = LocationPatron


@admin.action(description="Spoj lokality do poslední")
def merge_selected_last(model_admin, request, queryset, last=True):
    try:
        obj = Location.merge(queryset, last)
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id]
        )
        return HttpResponseRedirect(url)
    except AssertionError as e:
        messages.error(request, str(e))


@admin.action(description="Spoj lokality do první")
def merge_selected_first(model_admin, request, queryset):
    return merge_selected_last(model_admin, request, queryset, False)


@admin.register(Location)
class LocationAdmin(PermissionMixin, ModelAdmin):
    actions = [export_to_xlsx, merge_selected_first, merge_selected_last]
    inlines = (
        LocationContactPersonAdmin,
        LocationPatronAdmin,
        LocationPhotosAdmin,
    )
    search_fields = Location.get_search_fields()
    exclude = "_import_id", "_search_field"

    list_filter = (
        "program",
        "is_traditional",
        "for_beginners",
        "is_full",
        "is_unexplored",
        ("accessibility_from_prague", MultiSelectRelatedDropdownFilter),
        ("accessibility_from_brno", MultiSelectRelatedDropdownFilter),
        ("region", MultiSelectRelatedDropdownFilter),
    )

    formfield_overrides = {
        PointField: {"widget": LatLongWidget},
    }

    readonly_fields = ("get_events",)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not (
            request.user.is_superuser
            or request.user.is_office_worker
            or request.user.is_chairman
        ):
            del actions["merge_selected_first"]
            del actions["merge_selected_last"]
        return actions


class QualificationAdmin(PermissionMixin, NestedTabularInline):
    model = Qualification
    fk_name = "user"
    extra = 0
    readonly_fields = ("valid_till",)
    autocomplete_fields = ("approved_by",)
    exclude = ("_import_id",)
    empty_value_display = "Doplní se automaticky"


class QualificationNoteAdmin(PermissionMixin, NestedTabularInline):
    model = QualificationNote
    fk_name = "user"
    extra = 0
    autocomplete_fields = ("created_by",)
    empty_value_display = "Doplní se automaticky"


class UserEmailAdmin(PermissionMixin, SortableHiddenMixin, NestedTabularInline):
    model = UserEmail
    sortable_field_name = "order"
    extra = 0


class DuplicateUserAdminInline(PermissionMixin, NestedStackedInline):
    model = DuplicateUser
    fk_name = "user"
    autocomplete_fields = ("other",)
    extra = 0


class ClosePersonAdmin(PermissionMixin, NestedTabularInline):
    model = UserClosePerson


class UserAddressAdmin(PermissionMixin, NestedTabularInline):
    model = UserAddress


class UserContactAddressAdmin(PermissionMixin, NestedTabularInline):
    model = UserContactAddress


class EYCACardAdmin(PermissionMixin, NestedTabularInline):
    model = EYCACard


class DonorEventAdminInline(PermissionMixin, NestedTabularInline):
    model = DonorEvent
    fk_name = "user"
    extra = 0
    classes = ("collapse",)
    readonly_fields = ("created_at", "created_by")
    fields = (
        "event_type",
        "campaign",
        "fundraisers_note",
        "pledge",
        "reminder",
        "created_at",
        "created_by",
    )


class CompanyAdminInline(PermissionMixin, NestedTabularInline):
    model = Company
    extra = 0


class VariableSymbolAdminInline(PermissionMixin, NestedTabularInline):
    model = VariableSymbol
    extra = 0


class ReadOnlyInlineMixin:
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PledgeAdminInline(ReadOnlyInlineMixin, PermissionMixin, NestedTabularInline):
    model = Pledge
    classes = ("collapse",)
    fields = ("id", "donation_source", "is_recurrent", "recurrent_state", "pledged_at")


class DonationAdminInline(ReadOnlyInlineMixin, PermissionMixin, NestedTabularInline):
    model = Donation
    classes = ("collapse",)
    fields = ("donated_at", "amount", "donation_source", "info")


class DonorAdminInline(PermissionMixin, NestedStackedInline):
    model = Donor
    fk_name = "user"
    extra = 0
    exclude = ("subscribed_to_newsletter",)
    readonly_fields = ("get_donations_sum",)
    autocomplete_fields = ("regional_center_support", "basic_section_support")
    inlines = (
        CompanyAdminInline,
        VariableSymbolAdminInline,
        PledgeAdminInline,
        DonationAdminInline,
    )

    @admin.display(description="Suma darů")
    def get_donations_sum(self, obj):
        if obj.pk is None:
            return 0
        return obj.donations.aggregate(total=Coalesce(Sum("amount"), 0))["total"]


class UserOfferedHelpAdmin(PermissionMixin, NestedStackedInline):
    model = OfferedHelp
    classes = ("collapse",)


@admin.action(description="Označ vybrané mužským oslovením")
def mark_as_man(model_admin, request, queryset):
    perms = Permissions(request.user, User, "backend")
    if not all(perms.has_change_permission(obj) for obj in queryset):
        return model_admin.message_user(
            request, "Nemáš právo editovat vybrané objekty", ERROR
        )
    queryset.update(pronoun=PronounCategory.objects.get(slug="man"))


@admin.action(description="Označ vybrané ženským oslovením")
def mark_as_woman(model_admin, request, queryset):
    perms = Permissions(request.user, User, "backend")
    if not all(perms.has_change_permission(obj) for obj in queryset):
        return model_admin.message_user(
            request, "Nemáš právo editovat vybrané objekty", ERROR
        )
    queryset.update(pronoun=PronounCategory.objects.get(slug="woman"))


def get_member_action(membership_category, administration_unit):
    def action(view, request, queryset):
        for user in queryset:
            Membership.extend_for(
                request, user, membership_category, administration_unit
            )

    action.__name__ = f"add_member_{membership_category}_{administration_unit.id}"
    return action


def get_add_members_actions(administration_units):
    translate = {
        "family": "Nastav první rodinné členství",
        "family_member": "Nastav další rodinné členství",
        "individual": "Nastav individuální členství",
        "member_elsewhere": "Nastav, že platil členství v jiném ZČ",
        "extend": "Prodluž členství",
    }
    return [
        admin.action(
            description=f"{translate[membership_category]} "
            f"pro aktuální rok pod {administration_unit.abbreviation}"
        )(get_member_action(membership_category, administration_unit))
        for administration_unit in administration_units
        for membership_category in translate
    ]


CAMPAIGN_OPERATIONS = [
    ("added_to_campaign", "Přidat do kampaně"),
    ("remove", "Odebrat z kampaně"),
]


@admin.action(description="Změň členství v fundraisingové kampani…")
def change_fundraising_campaign(model_admin, request, queryset):
    if "apply" in request.POST:
        campaign_id = request.POST.get("campaign")
        operation_slug = request.POST.get("operation")

        try:
            campaign = FundraisingCampaign.objects.get(pk=campaign_id)
        except FundraisingCampaign.DoesNotExist:
            messages.error(request, "Vyberte kampaň.")
            return

        if operation_slug not in dict(CAMPAIGN_OPERATIONS):
            messages.error(request, "Vyberte operaci.")
            return

        added_type = DonorEventCategory.objects.get(slug="added_to_campaign")

        count = 0
        for user in queryset:
            membership_qs = DonorEvent.objects.filter(
                user=user, campaign=campaign, event_type=added_type
            )
            if operation_slug == "added_to_campaign":
                if not membership_qs.exists():
                    DonorEvent.objects.create(
                        user=user,
                        event_type=added_type,
                        campaign=campaign,
                        created_by=request.user,
                    )
                    count += 1
            else:
                membership = membership_qs.first()
                if membership:
                    other_events = DonorEvent.objects.filter(
                        user=user, campaign=campaign
                    ).exclude(pk=membership.pk)
                    if not other_events.exists():
                        membership.delete()
                        count += 1

        messages.success(request, f"Provedeno pro {count} osob v kampani {campaign}.")
        return

    return TemplateResponse(
        request,
        "donations/campaign_action.html",
        {
            "title": "Změnit členství v fundraisingové kampani",
            "queryset": queryset,
            "campaigns": FundraisingCampaign.objects.all(),
            "operations": CAMPAIGN_OPERATIONS,
            "action_name": "change_fundraising_campaign",
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "opts": model_admin.model._meta,
        },
    )


TAG_OPERATIONS = [
    ("add", "Přidat štítek"),
    ("remove", "Odebrat štítek"),
]


@admin.action(description="Přidat / odebrat dočasný štítek…")
def change_user_tag(model_admin, request, queryset):
    if not (request.user.is_superuser or request.user.is_office_worker):
        return model_admin.message_user(request, "Nemáš právo upravovat štítky", ERROR)

    if "apply" in request.POST:
        operation = request.POST.get("operation")
        name = (request.POST.get("name") or "").strip()

        if operation not in dict(TAG_OPERATIONS):
            messages.error(request, "Vyber operaci.")
            return
        if not name:
            messages.error(request, "Vyplň název štítku.")
            return

        tag = UserTag.objects.filter(name=name).first()

        if operation == "add":
            if tag is None:
                tag = UserTag.objects.create(name=name)
            tag.users.add(*queryset)
            messages.success(
                request,
                f"Přidán štítek „{tag}“ pro {queryset.count()} uživatelů.",
            )
        else:
            if tag is None:
                messages.error(request, f"Štítek „{name}“ neexistuje.")
                return
            tag.users.remove(*queryset)
            messages.success(
                request,
                f"Odebrán štítek „{tag}“ pro {queryset.count()} uživatelů.",
            )
        return

    return TemplateResponse(
        request,
        "bis/change_user_tag_action.html",
        {
            **model_admin.admin_site.each_context(request),
            "title": "Přidat / odebrat dočasný štítek",
            "queryset": queryset,
            "tags": UserTag.objects.order_by("name"),
            "operations": TAG_OPERATIONS,
            "action_name": "change_user_tag",
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "opts": model_admin.model._meta,
        },
    )


@action(description="Vypiš e-maily")
def export_emails(view, request, queryset):
    emails = queryset.values_list("email", flat=True)
    emails = [email for email in emails if email]

    return HttpResponse("<br>".join(emails))


def sees_donor_data(viewer, user):
    # The campaign history used to hang on the donor, so it stays visible to
    # exactly those who may see the person's donor profile.
    return viewer.can_see_all or visible_donors(viewer).filter(user=user).exists()


@admin.action(description="Zašli potvrzení o daru")
def send_donation_confirmation(model_admin, request, queryset):
    donors = visible_donors(request.user).filter(user__in=queryset.values("pk"))
    perms = Permissions(request.user, Donor, "backend")
    if not all(perms.has_change_permission(donor) for donor in donors):
        return model_admin.message_user(
            request, "Nemáš právo editovat vybrané objekty", ERROR
        )
    sent = 0
    for donor in donors:
        try:
            donation_confirmation(donor, *get_donation_confirmation(donor))
            sent += 1
        except AssertionError as e:
            messages.error(request, str(e))
    messages.info(request, f"Úspěšně posláno {sent} potvrzení")


@admin.action(description="Exportuj dárce")
def export_donors_to_xlsx(model_admin, request, queryset):
    donors = visible_donor_stats(request, model_admin).filter(
        user__in=queryset.values("pk")
    )
    return export_to_xlsx(model_admin, request, donors)


def annotate_visible_donor_stats(users, viewer):
    # Subqueries rather than joins, so postgres computes them only for the rows
    # on the page. They stay None for a user whose donor the viewer may not see.
    donor = visible_donors(viewer).filter(user=OuterRef("pk"))
    active_recurrent_pledges = Pledge.objects.filter(
        donor=OuterRef("pk"), is_recurrent=True, recurrent_state="collecting"
    )
    return users.annotate(
        donations_sum=Subquery(
            donor.annotate(total=Coalesce(Sum("donations__amount"), 0)).values("total")
        ),
        last_donation=Subquery(
            donor.annotate(last=Max("donations__donated_at")).values("last")
        ),
        has_active_recurrent_donation=Subquery(
            donor.annotate(recurrent=Exists(active_recurrent_pledges)).values(
                "recurrent"
            )
        ),
    )


@admin.register(User)
class UserAdmin(
    QuerySearchMixin,
    PermissionMixin,
    NestedModelAdminMixin,
    NumericFilterModelAdmin,
):
    change_form_template = "bis/user_change_form.html"
    actions = [
        export_to_xlsx,
        export_emails,
        mark_as_woman,
        mark_as_man,
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)

        administration_units = request.user.administration_units.all()
        for action_func in get_add_members_actions(administration_units):
            name = action_func.__name__
            actions[name] = (action_func, name, action_func.short_description)

        if request.user.is_superuser or request.user.is_office_worker:
            actions["change_user_tag"] = (
                change_user_tag,
                "change_user_tag",
                change_user_tag.short_description,
            )

        if Permissions(request.user, Donor, "backend").has_add_permission():
            actions["change_fundraising_campaign"] = (
                change_fundraising_campaign,
                "change_fundraising_campaign",
                change_fundraising_campaign.short_description,
            )

        if sees_donors(request.user):
            for action_func in [send_donation_confirmation, export_donors_to_xlsx]:
                name = action_func.__name__
                actions[name] = (action_func, name, action_func.short_description)

        return actions

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = (
            "is_superuser",
            "last_login",
            "date_joined",
            "get_all_emails",
            "get_events_where_was_organizer",
            "get_participated_in_events",
            "roles",
            "get_board_member_of",
            "get_token",
            "last_after_event_email",
            "is_contact_information_verified",
            "get_membership_actions",
            "create_membership",
        )
        if not request.user.is_superuser and not request.user.is_office_worker:
            readonly_fields += ("behaviour_issues",)

        return readonly_fields

    exclude = "groups", "user_permissions", "password", "is_superuser", "_str"

    fieldsets = (
        [
            None,
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "birth_name",
                    "nickname",
                    "birthday",
                    "pronoun",
                    "phone",
                    "get_all_emails",
                    "photo",
                ]
            },
        ],
        (
            "Osobní informace",
            {
                "fields": (
                    "health_insurance_company",
                    "health_issues",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Komunikace",
            {
                "fields": (
                    "subscription_status",
                    "do_not_call",
                    "do_not_solicit",
                    "do_not_send_after_event_email",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("models.Event.name_plural"),
            {
                "fields": (
                    "get_events_where_was_organizer",
                    "get_participated_in_events",
                )
            },
        ),
        (
            _("models.Membership.name"),
            {
                "fields": (
                    "get_membership_actions",
                    "create_membership",
                )
            },
        ),
        [
            "Interní data",
            {
                "fields": [
                    "roles",
                    "is_active",
                    "last_login",
                    "date_joined",
                    "last_after_event_email",
                    "is_contact_information_verified",
                    "get_board_member_of",
                    "vokativ",
                    "behaviour_issues",
                ],
                "classes": ("collapse",),
            },
        ],
    )
    ordering = "last_name", "first_name"

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser or request.user.is_office_worker:
            for header, data in fieldsets:
                if header == "Interní data":
                    if "office_workers_note" not in data["fields"]:
                        data["fields"].append("office_workers_note")

                    if request.user.is_superuser and "get_token" not in data["fields"]:
                        data["fields"] += [
                            "get_token",
                            "is_bot",
                            "sees_personal_data_over_mcp",
                        ]
                    break
            else:
                raise RuntimeError("Interní data not found in fieldsets")

        for header, data in fieldsets:
            if header is None:
                if obj and "email" in data["fields"]:
                    data["fields"].remove("email")

                if not obj and "email" not in data["fields"]:
                    data["fields"].insert(0, "email")
                break
        else:
            raise RuntimeError("First group not found in fieldsets")

        return fieldsets

    def get_list_display(self, request):
        columns = ["get_name", "get_links", "birthday", "address", "email", "phone"]
        match request.GET.get(ColumnsFilter.parameter_name):
            case "organizer":
                columns += ["get_qualifications", "get_memberships"]
            case "donor":
                columns += [
                    "get_donations_sum",
                    "get_last_donation",
                    "get_has_active_recurrent_donation",
                ]
        return columns

    list_filter = [
        ColumnsFilter,
        list_filter_extra_text(
            "Pokud chceš vybrat více možností u jednotho filtru (např.vybrat dva typy kvalifikace), "
            "přidrž tlačítko ctrl/shift"
        ),
        AgeFilter,
        list_filter_extra_title("Členství"),
        ("memberships__year", MemberDuringYearsFilter),
        ("memberships__id", MembershipCountFilter),
        MemberOfAdministrationUnitFilter,
        list_filter_extra_title("Hlavní organizátor"),
        ("events_where_was_as_main_organizer__start", MainOrganizerOfEventRangeFilter),
        (
            "events_where_was_as_main_organizer__id",
            EventsWhereWasAsMainOrganizerCountFilter,
        ),
        MainOrganizerOfEventOfAdministrationUnitFilter,
        list_filter_extra_title("Organizátor"),
        ("events_where_was_organizer__start", OrganizerOfEventRangeFilter),
        ("events_where_was_organizer__id", EventsWhereWasOrganizerCountFilter),
        OrganizerOfEventOfAdministrationUnitFilter,
        list_filter_extra_title("Účast na akcích"),
        ("participated_in_events__event__start", ParticipatedInEventRangeFilter),
        ("participated_in_events__id", ParticipatedInEventsCountFilter),
        ParticipatedInEventOfAdministrationUnitFilter,
        ("participated_in_events__event__end", FirstParticipatedInEventRangeFilter),
        list_filter_extra_title("Kvalifikace"),
        ("qualifications__valid_since", QualificationValidAtFilter),
        ("qualifications__category", QualificationCategoryFilter),
        list_filter_extra_title("Osobní info"),
        ("birthday", DateRangeFilter),
        NoBirthdayFilter,
        ("pronoun", MultiSelectRelatedDropdownFilter),
        ("address__region", MultiSelectRelatedDropdownFilter),
        ("health_insurance_company", MultiSelectRelatedDropdownFilter),
        list_filter_extra_title("Nabízená pomoc"),
        ("offers__programs", MultiSelectRelatedDropdownFilter),
        ("offers__organizer_roles", MultiSelectRelatedDropdownFilter),
        ("offers__team_roles", MultiSelectRelatedDropdownFilter),
        list_filter_extra_title("Kontaktování"),
        "subscription_status",
        "do_not_call",
        "do_not_solicit",
        "do_not_send_after_event_email",
        list_filter_extra_title("Ostatní"),
        ("roles", MultiSelectRelatedDropdownFilter),
        ("tags", MultiSelectRelatedDropdownFilter),
        ("date_joined", DateRangeFilter),
        ("chairman_of__existed_since", UserStatsDateFilter),
        NoLoginFilter,
        UserExportFilter,
    ]

    donor_list_filter = [
        list_filter_extra_title("Dárci"),
        IsDonorFilter,
        on_visible_donors(HasRecurrentDonationFilter),
        on_visible_donors(IsCompanyDonorFilter),
        on_visible_donors(
            AutocompleteFilterFactory("Podporující RC", "regional_center_support")
        ),
        on_visible_donors(
            AutocompleteFilterFactory("Podporující ZČ", "basic_section_support")
        ),
        ("donor", on_visible_donors(BooleanFieldListFilter, "is_public")),
        list_filter_extra_title("Dary"),
        (
            "donor",
            on_visible_donors(
                MultiSelectRelatedDropdownFilter, "donations__donation_source"
            ),
        ),
        list_filter_extra_note("Dary jen z vybraných zdrojů"),
        (
            "donor",
            on_visible_donors(FirstDonorsDonationFilter, "donations__donated_at"),
        ),
        list_filter_extra_note("První dan dárce (z vybraných zdrojů) z daného období"),
        ("donor", on_visible_donors(LastDonorsDonationFilter, "donations__donated_at")),
        list_filter_extra_note(
            "Poslední dan dárce (z vybraných zdrojů) z daného období"
        ),
        ("donor", on_visible_donors(DonationSumRangeFilter, "donations__donated_at")),
        list_filter_extra_note(
            "Dary pro celkovou sumu (z vybraných zdrojů) jen z daného období"
        ),
        ("donor", on_visible_donors(DonationSumAmountFilter, "donations__amount")),
        list_filter_extra_note(
            "Suma darů (z vybraných zdrojů) (z vybraného období) z daného rozmezí"
        ),
        on_visible_donors(RecurringDonorWhoStoppedFilter),
        list_filter_extra_title("Fundraisingové kampaně"),
        (
            "campaign_events__campaign",
            on_visible_campaign_history(MultiSelectRelatedDropdownFilter),
        ),
        (
            "campaign_events__event_type",
            on_visible_campaign_history(MultiSelectRelatedDropdownAndCampaignFilter),
        ),
        on_visible_campaign_history(HasPledgeInCampaignFilter),
    ]

    def get_list_filter(self, request):
        if sees_donors(request.user):
            return self.list_filter + self.donor_list_filter
        return self.list_filter

    search_fields = User.get_search_fields()
    list_select_related = "address", "contact_address"

    def get_inlines(self, request, obj):
        inlines = [
            UserAddressAdmin,
            UserContactAddressAdmin,
            ClosePersonAdmin,
            QualificationAdmin,
            QualificationNoteAdmin,
            UserOfferedHelpAdmin,
            EYCACardAdmin,
            DuplicateUserAdminInline,
        ]
        if obj and sees_donor_data(request.user, obj):
            inlines += [DonorAdminInline, DonorEventAdminInline]
        if request.user.is_superuser and obj:
            inlines.append(UserEmailAdmin)
        return inlines

    def get_rangefilter_participated_in_events__event__start_title(
        self, request, field_path
    ):
        return "Jeli na akci v období"

    def get_rangefilter_events_where_was_organizer__start_title(
        self, request, field_path
    ):
        return "Organizovali akci v období"

    def get_rangefilter_events_where_was_as_main_organizer__start_title(
        self, request, field_path
    ):
        return "Vedli akci v období"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        match request.GET.get(ColumnsFilter.parameter_name):
            case "organizer":
                return queryset.prefetch_related(
                    "memberships__administration_unit",
                    "memberships__category",
                    "qualifications__category",
                )
            case "donor":
                return annotate_visible_donor_stats(queryset, request.user)
        return queryset

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj is not None:
            # Only the change form renders these; in get_queryset they would
            # also load for every row of the changelist and of the xlsx export,
            # which reuses that queryset.
            prefetch_related_objects(
                [obj], "events_where_was_organizer", "participated_in_events__event"
            )
        return obj

    @admin.display(description="V předsednictvu organizačních jednotek")
    def get_board_member_of(self, obj):
        return mark_safe(
            ", ".join(
                [get_admin_edit_url(item) for item in obj.administration_units.all()]
            )
        )

    @admin.display(description="Token")
    def get_token(self, obj):
        return f"Token {obj.auth_token}"

    @admin.display(description="Suma darů", ordering=NullsLast("donations_sum"))
    def get_donations_sum(self, obj):
        return obj.donations_sum

    @admin.display(description="Poslední dar", ordering=NullsLast("last_donation"))
    def get_last_donation(self, obj):
        return obj.last_donation

    @admin.display(description="Pravidelný dárce", boolean=True)
    def get_has_active_recurrent_donation(self, obj):
        return obj.has_active_recurrent_donation

    @admin.display(description="Odkazy")
    def get_links(self, obj):
        return mark_safe(
            f'<a target="_blank" href="/profil/{obj.id}/" title="Zobrazit v BISu pro organizátory">📄</a><br>'
            f'<a target="_blank" href="/profil/{obj.id}/upravit" title="Upravit v BISu pro organizátory">📝</a><br>'
        )

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        if request.user.is_superuser or request.user.is_office_worker:
            form.base_fields["birthday"].required = False
        return form

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id and "_add_access" in request.POST:
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            obj = self.get_object(request, unquote(object_id), to_field)
            Qualification.objects.get_or_create(
                user=obj,
                category=QualificationCategory.objects.get(
                    slug="organizer_without_education"
                ),
                defaults=dict(
                    valid_since=today(),
                    approved_by=request.user,
                ),
            )
            self.message_user(request, "Přístup přidán")
            return HttpResponseRedirect(".")
        if object_id and "_donation_confirmation_pdf_export" in request.POST:
            donor = self.get_visible_donor(request, object_id)
            try:
                return FileResponse(
                    get_donation_confirmation(donor)[0], as_attachment=True
                )
            except AssertionError as e:
                messages.error(request, str(e))
                return HttpResponseRedirect(".")
        if object_id and "_donation_confirmation_pdf_email" in request.POST:
            donor = self.get_visible_donor(request, object_id)
            try:
                donation_confirmation(donor, *get_donation_confirmation(donor))
                messages.info(request, "Potvrzení o daru úspěšně odesláno")
            except AssertionError as e:
                messages.error(request, str(e))
            return HttpResponseRedirect(".")
        if response := Membership.process_action(request):
            return response
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_visible_donor(self, request, object_id):
        return get_object_or_404(
            visible_donors(request.user), user__id=unquote(object_id)
        )

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        context["has_visible_donor"] = (
            obj is not None and visible_donors(request.user).filter(user=obj).exists()
        )
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj
        )

    @admin.display(description="Všechna členství")
    def get_membership_actions(self, obj):
        perms = Permissions(self.request.user, Membership, "backend")
        memberships = perms.filter_queryset(obj.memberships.all())
        memberships = [
            (
                membership.category,
                membership.year,
                membership.administration_unit,
                membership.get_membership_actions(
                    membership, perms.has_change_permission(membership)
                ),
            )
            for membership in memberships
        ]
        return make_table(
            memberships, ["Kategorie", "Rok", "Organizační jednotka", "Akce"]
        )

    @admin.display(description="Přidej nové členství")
    def create_membership(self, obj):
        if obj._state.adding:
            return "Nejdřív ulož uživatele"
        url = reverse("admin:bis_membership_add")
        url += f"?user={obj.id}"
        return make_a("zde", url)


@admin.action(description="Prodluž členství")
def extend_memberships(model_admin, request, queryset):
    perms = Permissions(request.user, Membership, "backend")
    if not all(perms.has_change_permission(obj.user) for obj in queryset):
        return messages.error(request, "Nemáš právo editovat vybrané uživatele")

    for membership in queryset.all():
        membership.extend(request)


@action(description="Vypiš e-maily")
def export_membership_emails(view, request, queryset):
    emails = queryset.values_list("user__email", flat=True)
    emails = [email for email in emails if email]

    return HttpResponse("<br>".join(emails))


class MembershipAdminAddForm(forms.ModelForm):
    help_text = "Pokud uživatel nemá e-mailovou adresu, zadejte kombinaci jméno + příjmení + datum narození"

    email = forms.EmailField(
        required=False,
        label="E-mail",
        help_text="Pokud uživatele nelze nalézt, zadejte jeho e-mailovou adresu",
    )
    first_name = forms.CharField(
        required=False, max_length=63, label="Křestní jméno", help_text=help_text
    )
    last_name = forms.CharField(
        required=False, max_length=63, label="Příjmení", help_text=help_text
    )
    birthday = forms.DateField(
        required=False, label="Datum narození", help_text=help_text
    )
    category = forms.CharField(required=False)
    slug = forms.ChoiceField(
        choices=(
            ("individual", "Individuální"),
            ("family", "první rodinný člen"),
            ("family_member", "další rodinný člen"),
            ("member_elsewhere", "platil v jiném ZČ"),
        ),
        label="Typ",
    )

    class Meta:
        model = Membership
        fields = ()

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["category"] = None
        if self.errors:
            return cleaned_data
        # find user
        # if user, check if has access
        user_info_filled = (
            cleaned_data["first_name"]
            and cleaned_data["last_name"]
            and cleaned_data["birthday"]
        )
        if (
            not cleaned_data["user"]
            and not cleaned_data["email"]
            and not user_info_filled
        ):
            raise ValidationError(
                "Pokud není vybrán uživatel ani není vyplněn e-mail, musí být vyplněno "
                "křestní jméno i příjmení i datum narození."
            )

        if not cleaned_data["user"]:
            cleaned_data["user"] = User.objects.filter(
                all_emails__email=cleaned_data["email"]
            ).first()

        if not cleaned_data["user"]:
            cleaned_data["user"] = User.objects.filter(
                first_name=cleaned_data["first_name"],
                last_name=cleaned_data["last_name"],
                birthday=cleaned_data["birthday"],
            ).first()

        if not cleaned_data["user"]:
            # create user
            if not user_info_filled:
                raise ValidationError(
                    "Uživatel nenalezen, pokud chcete uživatele vytvořit, je nutno zadat "
                    "jméno + příjmení + datum narození"
                )

            cleaned_data["user"] = User.objects.create(
                email=cleaned_data["email"],
                first_name=cleaned_data["first_name"],
                last_name=cleaned_data["last_name"],
                birthday=cleaned_data["birthday"],
            )
        else:
            # found user, has access?
            perms = Permissions(self.request.user, User, "backend")
            queryset = perms.filter_queryset(User.objects.all())
            if cleaned_data["user"] not in queryset:
                if cleaned_data["user"].birthday:
                    if not cleaned_data["birthday"]:
                        raise ValidationError(
                            {
                                "birthday": "Uživatel v BISu existuje, ale nemáš k němu přístup. Prosím vyplň datum "
                                "narození pro ověření, že k němu přístup mít máš :)"
                            }
                        )

                    try:
                        key = f"{cleaned_data['user'].id}_{self.request.user.id}"
                        guess_birthday_throttle.check(key)
                    except Throttled as e:
                        raise ValidationError(str(e))

                    if cleaned_data["birthday"] != cleaned_data["user"].birthday:
                        guess_birthday_throttle.add(key)
                        raise ValidationError(
                            {
                                "birthday": "Uživatel v BISu existuje, ale jeho datum narození se neshoduje se "
                                "zadaným. Oprav datum narození nebo kontaktuj kancl (bis@brontosaurus.cz)"
                            }
                        )

        if cleaned_data["slug"] == "individual":
            if not cleaned_data["user"].birthday:
                if not cleaned_data["birthday"]:
                    raise ValidationError(
                        {
                            "birthday": "Nelze nastavit individuální členství, protože neznám datum narození. "
                            "Prosím vyplňte datum narození."
                        }
                    )
                cleaned_data["user"].birthday = cleaned_data["birthday"]
                User.objects.bulk_update([cleaned_data["user"]], ["birthday"])
            cleaned_data["slug"] = MembershipCategory.get_individual(
                cleaned_data["user"].birthday
            )
        cleaned_data["category"] = MembershipCategory.objects.get(
            slug=cleaned_data["slug"]
        )

        cleaned_data["year"] = cleaned_data["year"] or today().year
        allowed_years = [today().year]
        if today().month == 1:
            allowed_years.append(today().year - 1)
        if cleaned_data["year"] not in allowed_years:
            if not (
                self.request.user.is_superuser or self.request.user.is_office_worker
            ):
                raise ValidationError(
                    {"year": "Můžeš přidávat členství jen za tento rok"}
                )

        if (
            cleaned_data["administration_unit"]
            not in self.request.user.administration_units.all()
        ):
            if not (
                self.request.user.is_superuser or self.request.user.is_office_worker
            ):
                raise ValidationError(
                    {
                        "administration_unit": "Můžeš přidávat členství jen pod své organizační jednotky"
                    }
                )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].required = False
        self.fields["year"].required = False
        self.fields["category"].widget = self.fields["category"].hidden_widget()
        self.fields["category"].initial = MembershipCategory.objects.first()

        if au := self.request.user.administration_units.first():
            self.fields["administration_unit"].initial = au


@admin.register(Membership)
class MembershipAdmin(PermissionMixin, NestedModelAdmin):
    date_hierarchy = "_year"
    change_list_template = "bis/membership_change_list.html"
    exclude = ("_import_id", "_year")
    actions = [export_to_xlsx, extend_memberships, export_membership_emails]
    autocomplete_fields = "user", "administration_unit"

    search_fields = User.get_search_fields(prefix="user__")
    list_select_related = "administration_unit", "category", "user"
    hide_filters = True
    list_filter = [
        LatestMembershipOnlyFilter,
        AutocompleteFilterFactory("Organizační jednotka", "administration_unit"),
        ("category", MultiSelectRelatedDropdownFilter),
        ("year", MembershipYearFilter),
    ]

    list_display = [
        "get_user_link",
        "year",
        "category",
        "price",
        "administration_unit",
        "get_membership_actions",
    ]

    @admin.display(description="Uživatel")
    def get_user_link(self, obj):
        return make_a(
            obj.user,
            reverse("admin:bis_user_change", kwargs={"object_id": obj.user_id}),
        )

    @admin.display(description="Akce")
    def get_membership_actions(self, obj):
        can_change = Permissions(
            self.request.user, Membership, "backned"
        ).has_change_permission(obj)
        return Membership.get_membership_actions(obj, can_change)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if obj:
            return ["user", "administration_unit", "year"]

        return super().get_readonly_fields(request, obj)

    def changelist_view(self, request, extra_context=None):
        if response := Membership.process_action(request):
            return response
        return super().changelist_view(request, extra_context)

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            self.form = MembershipAdminAddForm
        else:
            self.form = forms.ModelForm
        form = super().get_form(request, obj, change, **kwargs)
        form.request = request
        return form

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [
                ["Vyhledání uživatele", {"fields": ("user",)}],
                [
                    "Pokud nelze najít uživatele",
                    {
                        "fields": ("email", "first_name", "last_name", "birthday"),
                        "classes": ("collapse",),
                    },
                ],
                [
                    "Členství",
                    {
                        "fields": (
                            "slug",
                            "administration_unit",
                            "year",
                            "category",
                        ),
                    },
                ],
            ]
        return super().get_fieldsets(request, obj)
