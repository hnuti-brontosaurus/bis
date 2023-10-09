from django.contrib import admin

from bis.admin_permissions import PermissionMixin
from categories.models import *


@admin.register(GrantCategory)
class GrantCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(EventIntendedForCategory)
class EventIntendedForCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(DietCategory)
class DietCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(QualificationCategory)
class QualificationCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = 'name', 'get_parents'

    @admin.display(description="Nadřazené kvalifikace")
    def get_parents(self, instance):
        return list(instance.parents.all())


@admin.register(AdministrationUnitCategory)
class AdministrationUnitCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(MembershipCategory)
class MembershipCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = 'name', 'price'


@admin.register(EventGroupCategory)
class EventGroupCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(EventCategory)
class EventCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(EventProgramCategory)
class EventProgramCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(DonationSourceCategory)
class DonationSourceCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(OrganizerRoleCategory)
class OrganizerRoleCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(TeamRoleCategory)
class TeamRoleCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(OpportunityCategory)
class OpportunityCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(LocationProgramCategory)
class LocationProgramCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(LocationAccessibilityCategory)
class LocationAccessibilityCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(RoleCategory)
class RoleCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(HealthInsuranceCompany)
class HealthInsuranceCompanyAdmin(PermissionMixin, admin.ModelAdmin):
    pass


@admin.register(PronounCategory)
class PronounCategoryAdmin(PermissionMixin, admin.ModelAdmin):
    pass
