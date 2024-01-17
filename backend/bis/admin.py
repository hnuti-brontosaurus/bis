from admin_auto_filters.filters import AutocompleteFilterFactory
from admin_numeric_filter.admin import NumericFilterModelAdmin, RangeNumericFilter
from administration_units.models import AdministrationUnit
from bis.admin_filters import (
    AgeFilter,
    FirstParticipatedInEventRangeFilter,
    MainOrganizerOfEventOfAdministrationUnitFilter,
    MainOrganizerOfEventRangeFilter,
    MemberDuringYearsFilter,
    MemberOfAdministrationUnitFilter,
    NoBirthdayFilter,
    OrganizerOfEventOfAdministrationUnitFilter,
    OrganizerOfEventRangeFilter,
    ParticipatedInEventOfAdministrationUnitFilter,
    ParticipatedInEventRangeFilter,
    QualificationCategoryFilter,
    QualificationValidAtFilter,
    UserStatsDateFilter,
)
from bis.admin_helpers import (
    LatestMembershipOnlyFilter,
    LatLongWidget,
    ShowDuplicateMembershipsFilter,
    get_admin_edit_url,
    list_filter_extra_text,
    list_filter_extra_title,
)
from bis.admin_permissions import PermissionMixin
from bis.helpers import make_a
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
from categories.models import PronounCategory
from dateutil.utils import today
from django import forms
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, action
from django.contrib.auth.models import Group
from django.contrib.gis.forms import PointField
from django.contrib.messages import ERROR
from django.core.exceptions import ValidationError
from django.db import ProgrammingError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from login_code.models import ThrottleLog
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import (
    NestedModelAdmin,
    NestedModelAdminMixin,
    NestedStackedInline,
    NestedTabularInline,
)
from opportunities.models import OfferedHelp
from other.models import DuplicateUser
from rangefilter.filters import DateRangeFilter
from rest_framework.authtoken.models import TokenProxy
from rest_framework.exceptions import Throttled
from translation.translate import _
from xlsx_export.export import export_to_xlsx

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
    actions = [merge_selected_first, merge_selected_last]
    inlines = (
        LocationContactPersonAdmin,
        LocationPatronAdmin,
        LocationPhotosAdmin,
    )
    search_fields = "name", "description"
    exclude = ("_import_id",)

    list_filter = (
        "program",
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
        if not (request.user.is_superuser or request.user.is_office_worker):
            del actions["merge_selected_first"]
            del actions["merge_selected_last"]
        return actions


class AllMembershipAdmin(PermissionMixin, NestedTabularInline):
    verbose_name_plural = "Všechna členství"
    model = Membership
    extra = 0
    autocomplete_fields = ("administration_unit",)
    exclude = ("_import_id",)
    readonly_fields = ("get_membership_actions",)

    @admin.display(description="Akce")
    def get_membership_actions(self, obj):
        if not obj.id:
            return ""
        can_change = Permissions(
            self.request.user, Membership, "backned"
        ).has_change_permission(obj)
        return Membership.get_membership_actions(obj, can_change, "<br>")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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


class UserOfferedHelpAdmin(PermissionMixin, NestedStackedInline):
    model = OfferedHelp
    classes = ("collapse",)


@admin.action(description="Označ vybrané mužským oslovením")
def mark_as_man(model_admin, request, queryset):
    perms = Permissions(request.user, User, "backend")
    if not all([perms.has_change_permission(obj) for obj in queryset]):
        return model_admin.message_user(
            request, "Nemáš právo editovat vybrané objekty", ERROR
        )
    queryset.update(pronoun=PronounCategory.objects.get(slug="man"))


@admin.action(description="Označ vybrané ženským oslovením")
def mark_as_woman(model_admin, request, queryset):
    perms = Permissions(request.user, User, "backend")
    if not all([perms.has_change_permission(obj) for obj in queryset]):
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


def get_add_members_actions():
    translate = {
        "family": "Nastav první rodinné členství",
        "family_member": "Nastav další rodinné členství",
        "individual": "Nastav individuální členství",
        "member_elsewhere": "Nastav, že platil členství v jiném ZČ",
        "extend": "Prodluž členství",
    }
    try:
        return [
            admin.action(
                description=f"{translate[membership_category]} "
                f"pro aktuální rok pod {administration_unit.abbreviation}"
            )(get_member_action(membership_category, administration_unit))
            for administration_unit in AdministrationUnit.objects.filter(
                existed_till__isnull=True
            )
            for membership_category in translate.keys()
        ]
    except ProgrammingError:
        return []


@action(description="Vypiš e-maily")
def export_emails(view, request, queryset):
    emails = queryset.values_list("email", flat=True)
    emails = [email for email in emails if email]

    return HttpResponse("<br>".join(emails))


@admin.register(User)
class UserAdmin(PermissionMixin, NestedModelAdminMixin, NumericFilterModelAdmin):
    actions = [
        export_to_xlsx,
        export_emails,
        mark_as_woman,
        mark_as_man,
    ] + get_add_members_actions()

    def get_actions(self, request):
        actions = super().get_actions(request)
        user_administration_units = request.user.administration_units.all()
        for key in list(actions.keys()):
            if "add_member" in key and not any(
                [key.endswith(f"_{au.id}") for au in user_administration_units]
            ):
                del actions[key]

        return actions

    readonly_fields = (
        "is_superuser",
        "last_login",
        "date_joined",
        "get_all_emails",
        "get_events_where_was_organizer",
        "get_participated_in_events",
        "roles",
        "get_donor",
        "get_board_member_of",
        "get_token",
        "last_after_event_email",
    )
    exclude = "groups", "user_permissions", "password", "is_superuser", "_str"

    fieldsets = (
        [
            None,
            {
                "fields": [
                    "get_donor",
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
                    "subscribed_to_newsletter",
                    "health_insurance_company",
                    "health_issues",
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
        [
            "Interní data",
            {
                "fields": [
                    "roles",
                    "is_active",
                    "last_login",
                    "date_joined",
                    "last_after_event_email",
                    "get_board_member_of",
                    "vokativ",
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
                    if "internal_note" not in data["fields"]:
                        data["fields"].append("internal_note")

                    if request.user.is_superuser and "get_token" not in data["fields"]:
                        data["fields"].append("get_token")
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

    list_display = (
        "get_name",
        "get_links",
        "birthday",
        "address",
        "email",
        "phone",
        "get_qualifications",
        "get_memberships",
    )

    list_filter = [
        list_filter_extra_text(
            "Pokud chceš vybrat více možností u jednotho filtru (např.vybrat dva typy kvalifikace), "
            "přidrž tlačítko ctrl/shift"
        ),
        AgeFilter,
        list_filter_extra_title("Členství"),
        ("memberships__year", MemberDuringYearsFilter),
        MemberOfAdministrationUnitFilter,
        list_filter_extra_title("Účast na akcích"),
        ("events_where_was_as_main_organizer__start", MainOrganizerOfEventRangeFilter),
        MainOrganizerOfEventOfAdministrationUnitFilter,
        ("events_where_was_organizer__start", OrganizerOfEventRangeFilter),
        OrganizerOfEventOfAdministrationUnitFilter,
        ("participated_in_events__event__start", ParticipatedInEventRangeFilter),
        ParticipatedInEventOfAdministrationUnitFilter,
        ("participated_in_events__event__end", FirstParticipatedInEventRangeFilter),
        list_filter_extra_title("Nabízená pomoc"),
        ("offers__programs", MultiSelectRelatedDropdownFilter),
        ("offers__organizer_roles", MultiSelectRelatedDropdownFilter),
        ("offers__team_roles", MultiSelectRelatedDropdownFilter),
        list_filter_extra_title("Kvalifikace"),
        ("qualifications__valid_since", QualificationValidAtFilter),
        ("qualifications__category", QualificationCategoryFilter),
        list_filter_extra_title("Osobní info"),
        ("birthday", DateRangeFilter),
        NoBirthdayFilter,
        ("pronoun", MultiSelectRelatedDropdownFilter),
        ("address__region", MultiSelectRelatedDropdownFilter),
        ("health_insurance_company", MultiSelectRelatedDropdownFilter),
        list_filter_extra_title("Ostatní"),
        ("roles", MultiSelectRelatedDropdownFilter),
        ("date_joined", DateRangeFilter),
        ("chairman_of__existed_since", UserStatsDateFilter),
    ]

    search_fields = (
        "all_emails__email",
        "phone",
        "first_name",
        "last_name",
        "nickname",
        "birth_name",
    )
    list_select_related = "address", "contact_address"

    def get_inlines(self, request, obj):
        inlines = [
            UserAddressAdmin,
            UserContactAddressAdmin,
            ClosePersonAdmin,
            QualificationAdmin,
            QualificationNoteAdmin,
            AllMembershipAdmin,
            UserOfferedHelpAdmin,
            EYCACardAdmin,
            DuplicateUserAdminInline,
        ]
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
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "memberships__administration_unit",
                "qualifications__category",
                "events_where_was_organizer",
                "participated_in_events__event",
                "memberships__category",
            )
        )

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
        if response := Membership.process_action(request):
            return response
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.action(description="Prodluž členství")
def extend_memberships(model_admin, request, queryset):
    perms = Permissions(request.user, Membership, "backend")
    if not all([perms.has_change_permission(obj.user) for obj in queryset]):
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

    class Meta:
        model = Membership
        fields = (
            "user",
            "email",
            "first_name",
            "last_name",
            "birthday",
            "year",
            "administration_unit",
            "category",
        )

    def clean(self):
        cleaned_data = super().clean()
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
                            "Uživatel v BISu existuje, ale nemáš k němu přístup. Prosím vyplň datum "
                            "narození pro ověření, že k němu přístup mít máš :)"
                        )

                    try:
                        key = f"{cleaned_data['user'].id}_{self.request.user.id}"
                        ThrottleLog.check_throttled("guess_birthday", key, 3, 24)
                    except Throttled as e:
                        raise ValidationError(str(e))

                    if cleaned_data["birthday"] != cleaned_data["user"].birthday:
                        raise ValidationError(
                            "Uživatel v BISu existuje, ale jeho datum narození se neshoduje se "
                            "zadaným. Oprav datum narození nebo kontaktuj kancl (bis@brontosaurus.cz)"
                        )

        if cleaned_data["year"] != today().year:
            if not self.request.user.is_superuser:
                raise ValidationError("Můžeš přidávat členství jen za tento rok")

        if (
            cleaned_data["administration_unit"]
            not in self.request.user.administration_units.all()
        ):
            if (
                not self.request.user.is_superuser
                or not self.request.user.is_office_worker
            ):
                raise ValidationError(
                    "Můžeš přidávat členství jen pod své organizační jednotky"
                )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].required = False
        self.fields["year"].required = False


@admin.register(Membership)
class MembershipAdmin(PermissionMixin, NestedModelAdmin):
    date_hierarchy = "created_at"
    change_list_template = "bis/membership_change_list.html"
    list_per_page = 1000
    exclude = ("_import_id",)
    actions = [extend_memberships, export_membership_emails]
    autocomplete_fields = "user", "administration_unit"

    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__nickname",
        "user__phone",
        "user__email",
    )

    list_filter = [
        LatestMembershipOnlyFilter,
        AutocompleteFilterFactory("Organizační jednotka", "administration_unit"),
        AutocompleteFilterFactory("Uživatel", "user"),
        ("category", MultiSelectRelatedDropdownFilter),
        ("year", RangeNumericFilter),
        ShowDuplicateMembershipsFilter,
    ]

    list_display = [
        "get_user_link",
        "year",
        "category",
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
        return Membership.get_membership_actions(obj, can_change, ", ")

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
