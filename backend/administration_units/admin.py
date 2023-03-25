from dateutil.utils import today
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils.safestring import mark_safe
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from solo.admin import SingletonModelAdmin

from administration_units.models import AdministrationUnit, BrontosaurusMovement, AdministrationUnitAddress, \
    AdministrationUnitContactAddress, GeneralMeeting
from bis.admin_filters import IsAdministrationUnitActiveFilter
from bis.admin_helpers import get_admin_list_url
from bis.admin_permissions import PermissionMixin
from bis.models import User
from common.history import show_history
from xlsx_export.export import export_to_xlsx


class AdministrationUnitAddressAdmin(PermissionMixin, NestedTabularInline):
    model = AdministrationUnitAddress


class AdministrationUnitContactAddressAdmin(PermissionMixin, NestedTabularInline):
    model = AdministrationUnitContactAddress


class GeneralMeetingAdmin(PermissionMixin, NestedTabularInline):
    model = GeneralMeeting
    extra = 1


@admin.register(AdministrationUnit)
class AdministrationUnitAdmin(PermissionMixin, OSMGeoAdmin):
    actions = [export_to_xlsx]
    list_display = 'abbreviation', 'is_active', 'address', 'phone', 'get_email', 'www', 'chairman', 'category'
    search_fields = 'abbreviation', 'name', 'address__city', 'address__street', 'address__zip_code', 'phone', 'email'
    list_filter = IsAdministrationUnitActiveFilter, 'category', 'is_for_kids', \
                  ('address__region', MultiSelectRelatedDropdownFilter)

    autocomplete_fields = 'chairman', 'vice_chairman', 'manager', 'board_members'

    exclude = '_import_id', '_history'
    list_select_related = 'address', 'chairman', 'category'
    readonly_fields = 'history', 'get_members', 'get_organizers'

    inlines = AdministrationUnitAddressAdmin, AdministrationUnitContactAddressAdmin, GeneralMeetingAdmin

    @admin.display(description='Je aktivní', boolean=True)
    def is_active(self, obj):
        return obj.existed_till is None

    @admin.display(description='Historie')
    def history(self, obj):
        return show_history(obj._history)

    @admin.display(description='E-mail')
    def get_email(self, obj):
        if not obj.email: return None
        name, host = obj.email.split('@')
        return mark_safe(f'{name}<br>@{host}')

    @admin.display(description='Uživatelé s platným členstvím v tomto OJ')
    def get_members(self, obj):
        return get_admin_list_url(User, 'link', {
            'memberships__administration_unit': obj.id,
            'memberships__year_from': today().year,
            'memberships__year_to': today().year,
        })

    @admin.display(description='Kvalifikovaní organizátoři s platným členstvím v tomto OJ')
    def get_organizers(self, obj):
        return get_admin_list_url(User, 'link', {
            'memberships__administration_unit': obj.id,
            'memberships__year_from': today().year,
            'memberships__year_to': today().year,
            'qualifications__valid_since__range__gte': today(),
        })

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()


@admin.register(BrontosaurusMovement)
class BrontosaurusMovementAdmin(PermissionMixin, SingletonModelAdmin):
    autocomplete_fields = 'director', 'finance_director', 'bis_administrators', 'office_workers', 'audit_committee', \
                          'executive_committee', 'education_members'
    readonly_fields = 'history',
    exclude = '_history',

    @admin.display(description='Historie')
    def history(self, obj):
        return show_history(obj._history)
