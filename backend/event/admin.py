from os.path import join
from pathlib import Path

import openpyxl
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from xlsx2html import xlsx2html

import pandas
import pdfkit
from admin_auto_filters.filters import AutocompleteFilterFactory
from django.http import FileResponse, HttpResponseRedirect
from django.utils.datetime_safe import date
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import NestedTabularInline, NestedModelAdmin, NestedStackedInline
from rangefilter.filters import DateRangeFilter

from bis.admin import export_emails
from bis.admin_filters import EventStatsDateFilter
from bis.admin_helpers import list_filter_extra_text
from bis.admin_permissions import PermissionMixin
from bis.helpers import AgeStats
from event.models import *
from questionnaire.admin import QuestionnaireAdmin, EventApplicationAdmin
from translation.translate import _
from xlsx_export.export import export_to_xlsx, get_attendance_list, get_attendance_list_data, export_files


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

    readonly_fields = 'get_participants_age_stats_event_start', 'get_participants_age_stats_year_start', 'get_participants_table'
    autocomplete_fields = 'participants',

    @admin.display(description='Statistika věku účastníků a organizátorů k začátku akce')
    def get_participants_age_stats_event_start(self, obj):
        return AgeStats('účastníků', obj.get_all_participants(), obj.event.start).as_table()

    @admin.display(description='Statistika věku účastníků a organizátorů k začátku roku')
    def get_participants_age_stats_year_start(self, obj):
        return AgeStats('účastníků', obj.get_all_participants(), date(obj.event.start.year, 1, 1)).as_table()

    @admin.display(description='E-maily účastníků a organizátorů')
    def get_participants_table(self, obj):
        def make_cell(item): return f'<td>{item}</td>'
        def make_row(items): return f'<tr>{"".join(make_cell(item) for item in items)}</tr>'

        # participants = obj.record.get_all_participants()
        # header = []
        # participants = []
        # rows = [make_row(row) for row in participants]
        # rows = [header] + rows

        html = [
            # f'<table>{"".join(rows)}</table>',
            '<input type="submit" value="Exportovat e-maily účastníků" name="_attendance_list_emails_export">',
            '<input type="submit" value="Exportovat e-maily účastníků a organizátorů" name="_attendance_list_all_emails_export">',
        ]
        return mark_safe("".join(html))

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
    change_form_template = 'bis/event_change_form.html'

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

    list_display = 'name', 'frontend_link', 'get_date', 'get_administration_units', 'location', 'category', 'program', \
        'get_participants_count', 'get_young_percentage', 'get_total_hours_worked', \
        'get_event_record_photos_uploaded', 'get_event_finance_receipts_uploaded'
    list_select_related = 'location', 'category', 'program', 'record'

    @admin.display(description="Odkaz")
    def frontend_link(self, obj):
        return mark_safe(f'<a href="/org/akce/{obj.id}">org.<br>přístup</a>')

    @admin.display(description=_('models.AdministrationUnit.name_plural'))
    def get_administration_units(self, obj):
        return mark_safe('<br>'.join([str(au) for au in obj.administration_units.all()]))

    @admin.display(description='Počet účastníků + organizátorů')
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

    def changeform_view(self, request, object_id=None, form_url="",
                        extra_context=None):
        if object_id:
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            obj = self.get_object(request, unquote(object_id), to_field)
            if "_attendance_list_xlsx_export" in request.POST:
                return get_attendance_list(obj)['xlsx']
            if "_attendance_list_pdf_export" in request.POST:
                return get_attendance_list(obj)['pdf']
            if "_participants_xlsx_export" in request.POST:
                return export_to_xlsx(self, request, obj.record.get_all_participants())
            if "_attendance_list_emails_export" in request.POST:
                return export_emails(..., ..., obj.record.participants.all())
            if "_attendance_list_all_emails_export" in request.POST:
                return export_emails(..., ..., obj.record.get_all_participants())
            if "_redirect_to_fe" in request.POST:
                return HttpResponseRedirect(f"/org/akce/{object_id}")
            if "_files_export" in request.POST:
                return export_files(obj)

        return super().changeform_view(request, object_id, form_url, extra_context)
