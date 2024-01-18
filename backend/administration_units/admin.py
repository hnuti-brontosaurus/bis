from datetime import date

from administration_units.models import (
    AdministrationSubUnit,
    AdministrationSubUnitAddress,
    AdministrationUnit,
    AdministrationUnitAddress,
    AdministrationUnitContactAddress,
    BrontosaurusMovement,
    GeneralMeeting,
)
from bis.admin_filters import IsAdministrationUnitActiveFilter
from bis.admin_helpers import LatLongWidget, get_admin_list_url
from bis.admin_permissions import PermissionMixin
from bis.helpers import MembershipStats, make_br
from bis.models import Membership, User
from common.history import show_history
from dateutil.utils import today
from django.contrib import admin
from django.contrib.gis.db.models import PointField
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.nested import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline,
)
from solo.admin import SingletonModelAdmin
from xlsx_export.export import export_to_xlsx


class AdministrationUnitAddressAdmin(PermissionMixin, NestedTabularInline):
    model = AdministrationUnitAddress


class AdministrationUnitContactAddressAdmin(PermissionMixin, NestedTabularInline):
    model = AdministrationUnitContactAddress


class GeneralMeetingAdmin(PermissionMixin, NestedTabularInline):
    model = GeneralMeeting
    extra = 1


class AdministrationSubUnitAddressAdmin(PermissionMixin, NestedTabularInline):
    model = AdministrationSubUnitAddress


class AdministrationSubUnitAdmin(PermissionMixin, NestedStackedInline):
    model = AdministrationSubUnit
    extra = 0
    formfield_overrides = {
        PointField: {"widget": LatLongWidget},
    }
    autocomplete_fields = "main_leader", "sub_leaders"
    exclude = ("_history",)
    readonly_fields = ("history",)
    inlines = (AdministrationSubUnitAddressAdmin,)

    @admin.display(description="Historie")
    def history(self, obj):
        return show_history(obj._history)


@admin.register(AdministrationUnit)
class AdministrationUnitAdmin(PermissionMixin, NestedModelAdmin):
    actions = [export_to_xlsx]
    list_display = (
        "abbreviation",
        "get_links",
        "is_active",
        "address",
        "phone",
        "email",
        "www",
        "chairman",
        "category",
    )
    search_fields = AdministrationUnit.get_search_fields()
    list_filter = (
        IsAdministrationUnitActiveFilter,
        "category",
        "is_for_kids",
        ("address__region", MultiSelectRelatedDropdownFilter),
    )
    formfield_overrides = {
        PointField: {"widget": LatLongWidget},
    }

    autocomplete_fields = "chairman", "vice_chairman", "manager", "board_members"

    exclude = "_import_id", "_history"
    list_select_related = "address", "chairman", "category"
    readonly_fields = "history", "get_members", "get_organizers", "get_membership_stats"

    inlines = (
        AdministrationUnitAddressAdmin,
        AdministrationUnitContactAddressAdmin,
        GeneralMeetingAdmin,
        AdministrationSubUnitAdmin,
    )

    @admin.display(description="")
    def get_links(self, obj):
        return make_br(
            [
                get_admin_list_url(
                    User,
                    "👪",
                    {
                        "memberships__administration_unit": obj.id,
                        "memberships__year_from": today().year,
                        "memberships__year_to": today().year,
                    },
                    title="Zobrazit aktuální členy",
                ),
                get_admin_list_url(
                    Membership,
                    "📄",
                    {
                        "administration_unit": obj.id,
                    },
                    title="Zobrazit čelnství",
                ),
            ]
        )

    @admin.display(description="Historie")
    def history(self, obj):
        return show_history(obj._history)

    @admin.display(description="Uživatelé s platným členstvím v tomto OJ")
    def get_members(self, obj):
        return get_admin_list_url(
            User,
            "link",
            {
                "memberships__administration_unit": obj.id,
                "memberships__year_from": today().year,
                "memberships__year_to": today().year,
            },
        )

    @admin.display(
        description="Kvalifikovaní organizátoři s platným členstvím v tomto OJ"
    )
    def get_organizers(self, obj):
        return get_admin_list_url(
            User,
            "link",
            {
                "memberships__administration_unit": obj.id,
                "memberships__year_from": today().year,
                "memberships__year_to": today().year,
                "qualifications__valid_since__range__gte": today(),
            },
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()

    @admin.display(description="Statistika členských příspěvků")
    def get_membership_stats(self, obj):
        year = date.today().year
        return MembershipStats(
            f"organizační jednotky {obj.abbreviation} za rok {year}",
            Membership.objects.filter(administration_unit=obj, year=year),
        ).as_table()


@admin.register(BrontosaurusMovement)
class BrontosaurusMovementAdmin(PermissionMixin, SingletonModelAdmin):
    autocomplete_fields = (
        "director",
        "finance_director",
        "bis_administrators",
        "office_workers",
        "audit_committee",
        "executive_committee",
        "education_members",
    )
    readonly_fields = ("history",)
    exclude = ("_history",)

    @admin.display(description="Historie")
    def history(self, obj):
        return show_history(obj._history)
