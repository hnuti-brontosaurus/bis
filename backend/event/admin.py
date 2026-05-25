from contextlib import nullcontext
from datetime import date

from admin_auto_filters.filters import AutocompleteFilterFactory
from bis.admin import export_emails
from bis.admin_filters import EventStatsDateFilter, HasFeedbackFilter
from bis.admin_helpers import list_filter_extra_text
from bis.admin_permissions import PermissionMixin
from bis.helpers import AgeStats, paused_validation
from bis.models import User
from django.contrib import admin
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from event.models import (
    Event,
    EventPropagation,
    EventRecord,
    EventRegistration,
    VIPEventPropagation,
)
from feedback.models import EventFeedback
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.nested import (
    NestedModelAdmin,
    NestedStackedInline,
)
from rangefilter.filters import DateRangeFilter
from translation.translate import _
from xlsx_export.export import (
    export_files,
    export_to_xlsx,
    get_attendance_list,
)


class EventPropagationAdmin(PermissionMixin, NestedStackedInline):
    model = EventPropagation
    classes = ("collapse",)

    exclude = ("_contact_url",)


class EventVIPPropagationAdmin(PermissionMixin, NestedStackedInline):
    model = VIPEventPropagation
    classes = ("collapse",)


class EventRegistrationAdmin(PermissionMixin, NestedStackedInline):
    model = EventRegistration
    classes = ("collapse",)


class EventRecordAdmin(PermissionMixin, NestedStackedInline):
    model = EventRecord

    readonly_fields = (
        "attendance_list_type",
        "get_participants_age_stats_event_start",
        "get_participants_age_stats_year_start",
    )
    autocomplete_fields = ("participants",)

    @admin.display(
        description="Statistika věku účastníků a organizátorů k začátku akce"
    )
    def get_participants_age_stats_event_start(self, obj):
        if obj.attendance_list_type != EventRecord.AttendanceListType.FULL_LIST:
            return "—"
        return AgeStats(
            "účastníků", obj.get_all_participants(), obj.event.start
        ).as_table()

    @admin.display(
        description="Statistika věku účastníků a organizátorů k začátku roku"
    )
    def get_participants_age_stats_year_start(self, obj):
        if obj.attendance_list_type != EventRecord.AttendanceListType.FULL_LIST:
            return "—"
        return AgeStats(
            "účastníků", obj.get_all_participants(), date(obj.event.start.year, 1, 1)
        ).as_table()

    def get_formset(self, request, obj=None, **kwargs):
        kwargs.update(
            {
                "help_texts": {
                    "get_participants_age_stats_year_start": "Pro podmínky dotací",
                }
            }
        )
        return super().get_formset(request, obj, **kwargs)


@admin.action(description="Zarchivovat akce")
def mark_as_archived(model_admin, request, queryset):
    queryset.update(is_archived=True)


@admin.action(description="Export ZV")
def export_feedbacks(model_admin, request, queryset):
    feedbacks = EventFeedback.objects.filter(event__in=queryset)
    return export_to_xlsx(model_admin, request, feedbacks)


@admin.register(Event)
class EventAdmin(PermissionMixin, NestedModelAdmin):
    change_form_template = "bis/event_change_form.html"

    actions = [mark_as_archived, export_to_xlsx, export_feedbacks]
    inlines = (
        EventPropagationAdmin,
        EventVIPPropagationAdmin,
        EventRegistrationAdmin,
        EventRecordAdmin,
    )
    filter_horizontal = ("other_organizers",)

    def has_add_permission(self, request, obj=None):
        return False

    list_filter = [
        list_filter_extra_text(
            "Pokud chceš vybrat více možností u jednotho filtru (např.vybrat dva typy kvalifikace), "
            "přidrž tlačítko ctrl/shift"
        ),
        AutocompleteFilterFactory(
            _("models.AdministrationUnit.name"), "administration_units"
        ),
        ("start", DateRangeFilter),
        ("end", DateRangeFilter),
        ("group", MultiSelectRelatedDropdownFilter),
        ("category", MultiSelectRelatedDropdownFilter),
        ("tags", MultiSelectRelatedDropdownFilter),
        ("program", MultiSelectRelatedDropdownFilter),
        "propagation__is_shown_on_web",
        ("intended_for", MultiSelectRelatedDropdownFilter),
        "is_canceled",
        "is_closed",
        "is_archived",
        HasFeedbackFilter,
        "registration__is_registration_required",
        "registration__is_event_full",
        "is_attendance_list_required",
        ("location__region", MultiSelectRelatedDropdownFilter),
        ("main_organizer__birthday", EventStatsDateFilter),
        ("administration_units", MultiSelectRelatedDropdownFilter),
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not (request.user.is_superuser or request.user.is_office_worker):
            del actions["mark_as_archived"]
        return actions

    list_display = (
        "name",
        "get_links",
        "get_date",
        "get_administration_units",
        "location",
        "get_participants_count",
        "get_young_percentage",
        "get_total_hours_worked",
        "program",
        "is_shown_on_web",
        "is_canceled",
        "is_closed",
        "category",
        "get_tags",
        "intended_for",
    )
    list_select_related = (
        "location",
        "category",
        "program",
        "record",
        "intended_for",
        "propagation",
    )

    @admin.display(description="")
    def get_links(self, obj):
        return mark_safe(
            f'<a target="_blank" href="/org/akce/{obj.id}" title="Zobrazit v BISu pro organizátory">📄</a><br>'
            f'<a target="_blank" href="/org/akce/{obj.id}/uzavrit" title="Zobrazit přihlášky / účastníky">👪</a><br>'
            f'<a target="_blank" href="https://brontosaurus.cz/akce/{obj.id}/" title="Zobrazit na webu">🌐</a><br>'
        )

    @admin.display(description=_("models.AdministrationUnit.name_plural"))
    def get_administration_units(self, obj):
        return mark_safe(
            "<br>".join([str(au) for au in obj.administration_units.all()])
        )

    @admin.display(description="Štítky")
    def get_tags(self, obj):
        return mark_safe("<br>".join([str(tag) for tag in obj.tags.all()]))

    @admin.display(description="Počet účastníků + organizátorů")
    def get_participants_count(self, obj):
        if not hasattr(obj, "record"):
            return None
        obj.record.event = obj
        return obj.record.get_participants_count()

    @admin.display(description="% do 26 let")
    def get_young_percentage(self, obj):
        if not hasattr(obj, "record"):
            return None
        obj.record.event = obj
        return obj.record.get_young_percentage()

    @admin.display(description="Odpracováno hodin")
    def get_total_hours_worked(self, obj):
        if not hasattr(obj, "record"):
            return None
        return obj.record.total_hours_worked

    @admin.display(description="Zobrazena na webu?", boolean=True)
    def is_shown_on_web(self, obj):
        if not hasattr(obj, "propagation"):
            return False
        return obj.propagation.is_shown_on_web

    def changelist_view(self, request, extra_context=None):
        request._is_changelist = True
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if getattr(request, "_is_changelist", False):
            qs = qs.prefetch_related(
                "administration_units",
                "other_organizers",
                "record__participants",
                "tags",
            )
        return qs

    date_hierarchy = "start"
    search_fields = Event.get_search_fields()
    readonly_fields = "duration", "created_by", "created_at", "closed_at"

    autocomplete_fields = (
        "main_organizer",
        "other_organizers",
        "location",
        "administration_units",
    )

    exclude = "_import_id", "_search_field"

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        user = request.user

        class F1(form):
            def clean(_self):
                super().clean()
                if not user.is_superuser and not user.is_office_worker:
                    if not any(
                        [
                            any(
                                au in user.administration_units.all()
                                for au in _self.cleaned_data.get(
                                    "administration_units", []
                                )
                            ),
                            _self.cleaned_data.get("main_organizer") == user,
                            user
                            in _self.cleaned_data.get("other_organizers", []).all(),
                        ]
                    ):
                        raise ValidationError(
                            "Akci musíš vytvořit pod svou organizační jednotkou nebo "
                            "musíš být v organizátorském týmu"
                        )

                return _self.cleaned_data

        return F1

    def save_related(self, request, form, formsets, change):
        guard = paused_validation if self.saving_raw(request) else nullcontext

        with guard():
            super().save_related(request, form, formsets, change)
            form.instance.save()

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id:
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            obj = self.get_object(request, unquote(object_id), to_field)
            has_record = hasattr(obj, "record")
            if "_attendance_list_xlsx_export" in request.POST:
                return get_attendance_list(obj, "xlsx")
            if "_attendance_list_pdf_export" in request.POST:
                return get_attendance_list(obj, "pdf")
            if "_participants_xlsx_export" in request.POST:
                return get_attendance_list(obj, "xlsx", True)
            if "_attendance_list_emails_export" in request.POST:
                participants = (
                    has_record and obj.record.participants.all()
                ) or User.objects.none()
                return export_emails(..., ..., participants)
            if "_attendance_list_all_emails_export" in request.POST:
                participants = (
                    has_record and obj.record.get_all_participants()
                ) or obj.other_organizers.all()
                return export_emails(..., ..., participants)
            if "_redirect_to_fe" in request.POST:
                return HttpResponseRedirect(f"/org/akce/{object_id}")
            if "_redirect_to_fe_attendance_list" in request.POST:
                return HttpResponseRedirect(f"/org/akce/{object_id}/uzavrit")
            if "_files_export" in request.POST:
                return export_files(obj)

        return super().changeform_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        if self.saving_raw(request):
            self.message_user(request, "Uloženo bez validace")
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)
