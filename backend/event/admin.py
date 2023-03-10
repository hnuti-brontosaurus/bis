from admin_auto_filters.filters import AutocompleteFilterFactory
from django.forms import BaseModelFormSet
from django.utils.datetime_safe import date
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import NestedTabularInline, NestedModelAdmin, NestedStackedInline
from rangefilter.filters import DateRangeFilter

from bis.admin_filters import EventStatsDateFilter
from bis.admin_helpers import list_filter_extra_text
from bis.admin_permissions import PermissionMixin
from bis.helpers import AgeStats
from event.models import *
from questionnaire.admin import QuestionnaireAdmin, EventApplicationAdmin
from translation.translate import _
from xlsx_export.export import export_to_xlsx


class EventPropagationImageAdmin(PermissionMixin, SortableHiddenMixin, NestedTabularInline):
    model = EventPropagationImage
    sortable_field_name = 'order'
    readonly_fields = 'image_tag',
    extra = 3
    classes = 'collapse',

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class New1(formset):
            def clean(_self):
                super().clean()
                forms = [form for form in _self.forms if form.is_valid()]
                forms = [form for form in forms if form.cleaned_data.get('image')]
                forms = [form for form in forms if not (_self.can_delete and _self._should_delete_form(form))]
                if len(forms) < 1 and request._event_propagation_needs_image:
                    raise ValidationError('Nutno nahrát alespoň jeden obrázek')

        return New1


class EventPhotoAdmin(PermissionMixin, NestedTabularInline):
    model = EventPhoto
    readonly_fields = 'photo_tag',
    extra = 3
    classes = 'collapse',


class AttendanceListPageAdmin(PermissionMixin, NestedTabularInline):
    model = EventAttendanceListPage
    extra = 3
    classes = 'collapse',


class EventContactAdmin(PermissionMixin, NestedTabularInline):
    model = EventContact
    classes = 'collapse',


class EventFinanceReceiptAdmin(PermissionMixin, NestedStackedInline):
    model = EventFinanceReceipt
    classes = 'collapse',


class EventFinanceAdmin(PermissionMixin, NestedStackedInline):
    model = EventFinance
    classes = 'collapse',

    exclude = 'grant_category', 'grant_amount', 'total_event_cost'

    inlines = EventFinanceReceiptAdmin,


class EventVIPPropagationAdmin(PermissionMixin, NestedStackedInline):
    model = VIPEventPropagation
    classes = 'collapse',


class EventPropagationAdmin(PermissionMixin, NestedStackedInline):
    model = EventPropagation
    inlines = EventPropagationImageAdmin,
    classes = 'collapse',

    exclude = '_contact_url',

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class New1(formset):
            def clean(_self):
                request._event_propagation_needs_image = (
                        bool(getattr(_self, 'cleaned_data', [True])[0])
                        and not (_self.can_delete and _self._should_delete_form(_self.forms[0]))
                )
                return super().clean()

        return New1


class EventRegistrationAdmin(PermissionMixin, NestedStackedInline):
    model = EventRegistration
    classes = 'collapse',
    inlines = QuestionnaireAdmin, EventApplicationAdmin


class EventRecordAdmin(PermissionMixin, NestedStackedInline):
    model = EventRecord
    inlines = EventPhotoAdmin, AttendanceListPageAdmin, EventContactAdmin

    readonly_fields = 'get_participants_age_stats_event_start', 'get_participants_age_stats_year_start'
    autocomplete_fields = 'participants',

    @admin.display(description='Statistika věku účastníků k začátku akce')
    def get_participants_age_stats_event_start(self, obj):
        return AgeStats('účastníků', obj.participants.all(), obj.event.start).as_table()

    @admin.display(description='Statistika věku účastníků k začátku roku')
    def get_participants_age_stats_year_start(self, obj):
        return AgeStats('účastníků', obj.participants.all(), date(obj.event.start.year, 1, 1)).as_table()

    def get_formset(self, request, obj=None, **kwargs):
        kwargs.update({'help_texts': {
            'get_participants_age_stats_year_start': 'Pro podmínky dotací',
        }})
        return super().get_formset(request, obj, **kwargs)

@admin.action(description='Uzavřít akce')
def mark_as_closed(model_admin, request, queryset):
    queryset.update(is_closed=True)


@admin.register(Event)
class EventAdmin(PermissionMixin, NestedModelAdmin):
    actions = [mark_as_closed, export_to_xlsx]
    inlines = EventFinanceAdmin, EventPropagationAdmin, EventVIPPropagationAdmin, EventRegistrationAdmin, EventRecordAdmin
    filter_horizontal = 'other_organizers',

    list_filter = [
        list_filter_extra_text("Pokud chceš vybrat více možností u jednotho filtru (např.vybrat dva typy kvalifikace), "
                               "přidrž tlačítko ctrl/shift"),
        AutocompleteFilterFactory(_('models.AdministrationUnit.name'), 'administration_units'),
        ('start', DateRangeFilter),
        ('end', DateRangeFilter),
        ('group', MultiSelectRelatedDropdownFilter),
        ('category', MultiSelectRelatedDropdownFilter),
        ('program', MultiSelectRelatedDropdownFilter),
        'propagation__is_shown_on_web',
        ('intended_for', MultiSelectRelatedDropdownFilter),
        'is_canceled',
        'is_complete',
        'is_closed',
        'registration__is_registration_required',
        'registration__is_event_full',
        'is_attendance_list_required',
        ('location__region', MultiSelectRelatedDropdownFilter),
        ('main_organizer__birthday', EventStatsDateFilter),
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not (request.user.is_superuser or request.user.is_office_worker):
            del actions['mark_as_closed']
        return actions

    list_display = 'name', 'get_date', 'get_administration_units', 'location', 'category', 'program', \
        'get_participants_count', 'get_young_percentage', 'get_total_hours_worked', \
        'get_event_record_photos_uploaded', 'get_event_finance_receipts_uploaded'
    list_select_related = 'location', 'category', 'program', 'record'

    @admin.display(description=_('models.AdministrationUnit.name_plural'))
    def get_administration_units(self, obj):
        return mark_safe('<br>'.join([str(au) for au in obj.administration_units.all()]))

    @admin.display(description='Počet účastníků')
    def get_participants_count(self, obj):
        if not hasattr(obj, 'record'): return None
        return obj.record.get_participants_count()

    @admin.display(description='% do 26 let')
    def get_young_percentage(self, obj):
        if not hasattr(obj, 'record'): return None
        return obj.record.get_young_percentage()

    @admin.display(description='Odpracováno hodin')
    def get_total_hours_worked(self, obj):
        if not hasattr(obj, 'record'): return None
        return obj.record.total_hours_worked

    @admin.display(description='Fotky nahrány?', boolean=True)
    def get_event_record_photos_uploaded(self, obj):
        if not hasattr(obj, 'record'): return False
        return bool(len(obj.record.photos.all()))

    @admin.display(description='Účtenky nahrány?', boolean=True)
    def get_event_finance_receipts_uploaded(self, obj):
        if not hasattr(obj, 'finance'): return False
        return bool(len(obj.finance.receipts.all()))

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('administration_units', 'record__participants',
                                                              'record__photos', 'finance__receipts')

    date_hierarchy = 'start'
    search_fields = 'name',
    readonly_fields = 'duration',

    autocomplete_fields = 'main_organizer', 'other_organizers', 'location', 'administration_units',

    exclude = '_import_id',

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(EventAdmin, self).get_form(request, obj, change, **kwargs)
        user = request.user

        class F1(form):
            def clean(_self):
                super().clean()
                if not user.is_superuser and not user.is_office_worker:
                    if not any([
                        any([au in user.administration_units.all() for au in
                             _self.cleaned_data.get('administration_units', [])]),
                        _self.cleaned_data.get('main_organizer') == user,
                        user in _self.cleaned_data.get('other_organizers', []).all(),
                    ]):
                        raise ValidationError('Akci musíš vytvořit pod svou organizační jednotkou nebo '
                                              'musíš být v organizátorském týmu')

                return _self.cleaned_data

        return F1

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()
