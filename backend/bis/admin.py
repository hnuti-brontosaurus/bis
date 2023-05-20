from admin_numeric_filter.admin import NumericFilterModelAdmin
from dateutil.utils import today
from django.contrib import messages
from django.contrib.admin import action
from django.contrib.auth.models import Group
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.messages import ERROR
from django.db import ProgrammingError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import NestedTabularInline, NestedStackedInline, NestedModelAdminMixin
from rangefilter.filters import DateRangeFilter
from rest_framework.authtoken.models import TokenProxy

from bis.admin_filters import AgeFilter, NoBirthdayFilter, MainOrganizerOfEventRangeFilter, \
    OrganizerOfEventRangeFilter, ParticipatedInEventRangeFilter, MainOrganizerOfEventOfAdministrationUnitFilter, \
    OrganizerOfEventOfAdministrationUnitFilter, ParticipatedInEventOfAdministrationUnitFilter, MemberDuringYearsFilter, \
    MemberOfAdministrationUnitFilter, QualificationCategoryFilter, QualificationValidAtFilter, UserStatsDateFilter, \
    FirstParticipatedInEventRangeFilter
from bis.admin_helpers import list_filter_extra_title, list_filter_extra_text
from bis.admin_permissions import PermissionMixin
from bis.models import *
from opportunities.models import OfferedHelp
from other.models import DuplicateUser
from translation.translate import _
from xlsx_export.export import export_to_xlsx

admin.site.unregister(TokenProxy)
admin.site.unregister(Group)


class LocationPhotosAdmin(PermissionMixin, NestedTabularInline):
    model = LocationPhoto
    readonly_fields = 'photo_tag',


class LocationContactPersonAdmin(PermissionMixin, NestedTabularInline):
    model = LocationContactPerson


class LocationPatronAdmin(PermissionMixin, NestedTabularInline):
    model = LocationPatron

@admin.action(description='Spoj lokality do poslední')
def merge_selected_last(model_admin, request, queryset, last=True):
    try:
        obj = Location.merge(queryset, last)
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id])
        return HttpResponseRedirect(url)
    except AssertionError as e:
        messages.error(request, str(e))

@admin.action(description='Spoj lokality do první')
def merge_selected_first(model_admin, request, queryset):
    return merge_selected_last(model_admin, request, queryset, False)

@admin.register(Location)
class LocationAdmin(PermissionMixin, OSMGeoAdmin):
    actions = [merge_selected_first, merge_selected_last]
    inlines = LocationContactPersonAdmin, LocationPatronAdmin, LocationPhotosAdmin,
    search_fields = 'name', 'description'
    exclude = '_import_id',

    list_filter = 'program', 'for_beginners', 'is_full', 'is_unexplored', \
        ('accessibility_from_prague', MultiSelectRelatedDropdownFilter), \
        ('accessibility_from_brno', MultiSelectRelatedDropdownFilter), \
        ('region', MultiSelectRelatedDropdownFilter)

    readonly_fields = 'get_events',

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not (request.user.is_superuser or request.user.is_office_worker):
            del actions['merge_selected_first']
            del actions['merge_selected_last']
        return actions


class AllMembershipAdmin(PermissionMixin, NestedTabularInline):
    verbose_name_plural = 'Všechna členství'
    model = Membership
    extra = 0
    autocomplete_fields = 'administration_unit',
    exclude = '_import_id',

    def has_add_permission(self, request, obj=None): return request.user.is_superuser

    def has_change_permission(self, request, obj=None): return request.user.is_superuser

    def has_delete_permission(self, request, obj=None): return request.user.is_superuser


class MembershipAdmin(PermissionMixin, NestedTabularInline):
    verbose_name_plural = 'Členství za tento rok'
    model = Membership
    extra = 0
    autocomplete_fields = 'administration_unit',
    exclude = '_import_id',

    def get_queryset(self, request):
        queryset = super().get_queryset(request).filter(year=today().year)
        if not request.user.is_superuser:
            queryset = queryset.filter(administration_unit__in=request.user.administration_units.all())
        return queryset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(MembershipAdmin, self).get_formset(request, obj, **kwargs)

        class Formset(formset):
            def clean(_self):
                super().clean()
                forms = [form for form in _self.forms if form.is_valid()]
                forms = [form for form in forms if not (_self.can_delete and _self._should_delete_form(form))]
                forms = [form for form in forms if not request.user.is_superuser]

                for form in forms:
                    if form.instance.year != today().year:
                        raise ValidationError('Můžeš editovat členství jen za tento rok')
                    if form.instance.administration_unit not in request.user.administration_units.all():
                        raise ValidationError('Můžeš přidat členství jen ke své organizační jednotce')

        return Formset


class QualificationAdmin(PermissionMixin, NestedTabularInline):
    model = Qualification
    fk_name = 'user'
    extra = 0
    readonly_fields = 'valid_till',
    autocomplete_fields = 'approved_by',
    exclude = '_import_id',
    empty_value_display = 'Doplní se automaticky'


class UserEmailAdmin(PermissionMixin, SortableHiddenMixin, NestedTabularInline):
    model = UserEmail
    sortable_field_name = 'order'
    extra = 0


class DuplicateUserAdminInline(PermissionMixin, NestedStackedInline):
    model = DuplicateUser
    fk_name = 'user'
    autocomplete_fields = 'other',
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
    classes = 'collapse',


@admin.action(description='Označ vybrané mužským oslovením')
def mark_as_man(model_admin, request, queryset):
    if not all([obj.has_edit_permission(request.user) for obj in queryset]):
        return model_admin.message_user(request, 'Nemáš právo editovat vybrané objekty', ERROR)
    queryset.update(pronoun=PronounCategory.objects.get(slug='man'))


@admin.action(description='Označ vybrané ženským oslovením')
def mark_as_woman(model_admin, request, queryset):
    if not all([obj.has_edit_permission(request.user) for obj in queryset]):
        return model_admin.message_user(request, 'Nemáš právo editovat vybrané objekty', ERROR)
    queryset.update(pronoun=PronounCategory.objects.get(slug='woman'))


def get_member_action(membership_category, administration_unit):
    def action(view, request, queryset):
        categories = {c.slug: c for c in MembershipCategory.objects.all()}
        for user in queryset:
            slug = membership_category
            if slug == 'extend':
                previous = Membership.objects.filter(user=user, administration_unit=administration_unit, year=today().year-1).first()
                if not previous:
                    messages.error(request, f"Nelze prodloužit členství pro {user}, neb minulý rok nebyl/a členem {administration_unit}")
                    continue

                slug = previous.category.slug
                if slug in ["kid", "student", "adult"]:
                    slug = 'individual'

            if slug == "individual":
                slug = MembershipCategory.get_individual(user)

                if not slug:
                    messages.error(request, f"Nelze nastavit individuální členství pro {user}, neb není znám jeho/její věk")
                    continue

            Membership.objects.update_or_create(
                user=user,
                administration_unit=administration_unit,
                year=today().year,
                defaults=dict(category=categories[slug])
            )

    action.__name__ = f'add_member_{membership_category}_{administration_unit.id}'
    return action


def get_add_members_actions():
    translate = {
        "family": "Nastav první rodinné",
        "family_member": "Nastav další rodinné",
        "individual": "Nastav individuální",
        "extend": "Prodluž",
    }
    try:
        return [
            admin.action(
                description=f'{translate[membership_category]} členství '
                            f'na tento rok pod {administration_unit.abbreviation}'
            )(get_member_action(membership_category, administration_unit))
            for administration_unit in AdministrationUnit.objects.filter(existed_till__isnull=True)
            for membership_category in ["family", "family_member", "individual", "extend"]
        ]
    except ProgrammingError:
        return []


@action(description='Vypiš e-maily')
def export_emails(view, request, queryset):
    emails = queryset.values_list('email', flat=True)
    emails = [email for email in emails if email]

    return HttpResponse('<br>'.join(emails))


@admin.register(User)
class UserAdmin(PermissionMixin, NestedModelAdminMixin, NumericFilterModelAdmin):
    actions = [export_to_xlsx, export_emails, mark_as_woman, mark_as_man] + get_add_members_actions()

    def get_actions(self, request):
        actions = super().get_actions(request)
        user_administration_units = request.user.administration_units.all()
        for key in list(actions.keys()):
            if 'add_member' in key and not any([key.endswith(f'_{au.id}') for au in user_administration_units]):
                del actions[key]

        return actions

    readonly_fields = 'is_superuser', 'last_login', 'date_joined', 'get_all_emails', \
        'get_events_where_was_organizer', 'get_participated_in_events', \
        'roles', 'get_donor', 'get_board_member_of'
    exclude = 'groups', 'user_permissions', 'password', 'is_superuser', '_str'

    fieldsets = (
        [None, {
            'fields': ['get_donor', 'first_name', 'last_name', 'birth_name', 'nickname', 'birthday', 'pronoun', 'phone',
                       'get_all_emails']
        }],
        ('Osobní informace', {
            'fields': ('subscribed_to_newsletter', 'health_insurance_company', 'health_issues'),
            'classes': ('collapse',)
        }),
        (_('models.Event.name_plural'), {
            'fields': ('get_events_where_was_organizer', 'get_participated_in_events')
        }),
        ['Interní data', {
            'fields': ['roles', 'is_active', 'last_login', 'date_joined', 'get_board_member_of', 'vokativ'],
            'classes': ('collapse',)
        }]
    )
    ordering = "last_name", "first_name"

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser or request.user.is_office_worker:
            for header, data in fieldsets:
                if header == 'Interní data':
                    if 'internal_note' not in data['fields']:
                        data['fields'].append('internal_note')
                    break
            else:
                raise RuntimeError('Interní data not found in fieldsets')

        for header, data in fieldsets:
            if header is None:
                if obj and 'email' in data['fields']:
                    data['fields'].remove('email')

                if not obj and 'email' not in data['fields']:
                    data['fields'].insert(0, 'email')
                break
        else:
            raise RuntimeError('First group not found in fieldsets')


        return fieldsets

    list_display = 'get_name', 'birthday', 'address', 'get_email', 'phone', 'get_qualifications', 'get_memberships'

    list_filter = [
        list_filter_extra_text("Pokud chceš vybrat více možností u jednotho filtru (např.vybrat dva typy kvalifikace), "
                               "přidrž tlačítko ctrl/shift"),
        AgeFilter,

        list_filter_extra_title('Členství'),
        ('memberships__year', MemberDuringYearsFilter),
        MemberOfAdministrationUnitFilter,

        list_filter_extra_title('Účast na akcích'),
        ('events_where_was_as_main_organizer__start', MainOrganizerOfEventRangeFilter),
        MainOrganizerOfEventOfAdministrationUnitFilter,
        ('events_where_was_organizer__start', OrganizerOfEventRangeFilter),
        OrganizerOfEventOfAdministrationUnitFilter,
        ('participated_in_events__event__start', ParticipatedInEventRangeFilter),
        ParticipatedInEventOfAdministrationUnitFilter,
        ('participated_in_events__event__end', FirstParticipatedInEventRangeFilter),

        list_filter_extra_title('Nabízená pomoc'),
        ('offers__programs', MultiSelectRelatedDropdownFilter),
        ('offers__organizer_roles', MultiSelectRelatedDropdownFilter),
        ('offers__team_roles', MultiSelectRelatedDropdownFilter),

        list_filter_extra_title('Kvalifikace'),
        ('qualifications__valid_since', QualificationValidAtFilter),
        ('qualifications__category', QualificationCategoryFilter),

        list_filter_extra_title('Osobní info'),
        ('birthday', DateRangeFilter),
        NoBirthdayFilter,
        ('pronoun', MultiSelectRelatedDropdownFilter),
        ('address__region', MultiSelectRelatedDropdownFilter),
        ('health_insurance_company', MultiSelectRelatedDropdownFilter),

        list_filter_extra_title('Ostatní'),
        ('roles', MultiSelectRelatedDropdownFilter),
        ('date_joined', DateRangeFilter),
        ('chairman_of__existed_since', UserStatsDateFilter),
    ]

    search_fields = 'all_emails__email', 'phone', 'first_name', 'last_name', 'nickname', 'birth_name'
    list_select_related = 'address', 'contact_address'

    def get_inlines(self, request, obj):
        inlines = [UserAddressAdmin, UserContactAddressAdmin,
                   ClosePersonAdmin,
                   QualificationAdmin, AllMembershipAdmin, MembershipAdmin,
                   UserOfferedHelpAdmin,
                   EYCACardAdmin,
                   DuplicateUserAdminInline]
        if request.user.is_superuser and obj:
            inlines.append(UserEmailAdmin)
        return inlines

    def get_rangefilter_participated_in_events__event__start_title(self, request, field_path):
        return 'Jeli na akci v období'

    def get_rangefilter_events_where_was_organizer__start_title(self, request, field_path):
        return 'Organizovali akci v období'

    def get_rangefilter_events_where_was_as_main_organizer__start_title(self, request, field_path):
        return 'Vedli akci v období'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'memberships__administration_unit', 'qualifications__category',
            'events_where_was_organizer', 'participated_in_events__event', 'memberships__category'
        )

    @admin.display(description='V předsednictvu organizačních jednotek')
    def get_board_member_of(self, obj):
        return mark_safe(', '.join([get_admin_edit_url(item) for item in obj.administration_units.all()]))
