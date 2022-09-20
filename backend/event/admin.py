
from admin_auto_filters.filters import AutocompleteFilterFactory
from django.utils.datetime_safe import date
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import NestedTabularInline, NestedModelAdmin, NestedStackedInline
from rangefilter.filters import DateRangeFilter

from bis.admin_filters import EventStatsDateFilter
from bis.admin_permissions import PermissionMixin
from bis.helpers import AgeStats
from event.models import *
from questionnaire.admin import QuestionnaireAdmin, EventApplicationAdmin
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
                forms = [form for form in forms if not form.cleaned_data.get('DELETE', False)]
                if len(forms) < 1:
                    raise ValidationError('Nutno nahrát alespoň jeden obrázek')

        if '_saveasnew' not in request.POST:
            return New1

        id = request.resolver_match.kwargs['object_id']
        event = Event.objects.get(id=id)

        if not hasattr(event, 'propagation'):
            return New1

        images = event.propagation.images.all()

        class New(New1):
            def is_valid(_self):
                for i, form in enumerate(_self):
                    if i >= len(images):
                        continue

                    form.instance.image = images[i].image
                    form.fields['image'].required = False

                return super(New, _self).is_valid()

        return New


class EventPhotoAdmin(PermissionMixin, NestedTabularInline):
    model = EventPhoto
    readonly_fields = 'photo_tag',
    extra = 3
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
    inlines = EventVIPPropagationAdmin, EventPropagationImageAdmin,
    classes = 'collapse',

    autocomplete_fields = 'contact_person',

    exclude = '_contact_url',


class EventRegistrationAdmin(PermissionMixin, NestedStackedInline):
    model = EventRegistration
    classes = 'collapse',
    inlines = QuestionnaireAdmin, EventApplicationAdmin


class EventRecordAdmin(PermissionMixin, NestedStackedInline):
    model = EventRecord
    inlines = EventPhotoAdmin,
    classes = 'collapse',

    readonly_fields = 'get_participants_age_stats_event_start', 'get_participants_age_stats_year_start'
    autocomplete_fields = 'participants',

    @admin.display(description='Statistika věku účastníků k začátku akce')
    def get_participants_age_stats_event_start(self, obj):
        return AgeStats('účastníků', obj.participants.all(), obj.event.start.date()).as_table()

    @admin.display(description='Statistika věku účastníků k začátku roku')
    def get_participants_age_stats_year_start(self, obj):
        return AgeStats('účastníků', obj.participants.all(), date(obj.event.start.year, 1, 1)).as_table()

    def get_formset(self, request, obj=None, **kwargs):
        kwargs.update({'help_texts': {
            'get_participants_age_stats_year_start': 'Pro podmínky dotací',
        }})
        return super().get_formset(request, obj, **kwargs)


@admin.register(Event)
class EventAdmin(PermissionMixin, NestedModelAdmin):
    actions = [export_to_xlsx]
    inlines = EventFinanceAdmin, EventPropagationAdmin, EventRegistrationAdmin, EventRecordAdmin
    save_as = True
    filter_horizontal = 'other_organizers',

    list_filter = [
        AutocompleteFilterFactory('Zorganizováno pod', 'administration_units'),
        ('start', DateRangeFilter),
        ('end', DateRangeFilter),
        ('category', MultiSelectRelatedDropdownFilter),
        ('program', MultiSelectRelatedDropdownFilter),
        'propagation__is_shown_on_web',
        ('propagation__intended_for', MultiSelectRelatedDropdownFilter),
        'is_canceled',
        'is_internal',
        'registration__is_registration_required',
        'registration__is_event_full',
        'is_attendance_list_required',
        ('location__region', MultiSelectRelatedDropdownFilter),
        ('main_organizer__birthday', EventStatsDateFilter),
    ]

    list_display = 'name', 'get_date', 'get_administration_units', 'location', 'category', 'program', \
                   'get_participants_count', 'get_young_percentage', 'get_total_hours_worked', \
                   'get_event_record_photos_uploaded', 'get_event_finance_receipts_uploaded'
    list_select_related = 'location', 'category', 'program', 'record'

    @admin.display(description='Administrativní jednotky')
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
                        raise ValidationError('Akci musíš vytvořit pod svým článkem nebo '
                                              'musíš být v organizátorském týmu')

                return _self.cleaned_data

        if '_saveasnew' not in request.POST:
            return F1

        id = request.resolver_match.kwargs['object_id']
        event = Event.objects.get(id=id)

        class F2(F1):
            def clean(_self):
                super().clean()
                start = _self.cleaned_data['start']
                end = _self.cleaned_data['end']

                if start == event.start or end == event.end:
                    raise ValidationError("Nová událost musí mít odlišný čas začátku a konce od původní události")

                return _self.cleaned_data

        return F2

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()
