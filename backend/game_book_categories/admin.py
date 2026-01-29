from django.contrib import admin
from nested_admin.nested import NestedModelAdmin

from bis.admin_permissions import PermissionMixin
from game_book_categories.models import *


@admin.register(Tag)
class TagAdmin(PermissionMixin, NestedModelAdmin):
    list_display = ("name",)


@admin.register(PhysicalCategory)
class PhysicalCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"


@admin.register(MentalCategory)
class MentalCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"


@admin.register(LocationCategory)
class LocationCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"


@admin.register(ParticipantNumberCategory)
class ParticipantNumberCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"


@admin.register(ParticipantAgeCategory)
class ParticipantAgeCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"


@admin.register(GameLengthCategory)
class GameLengthCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"


@admin.register(PreparationLengthCategory)
class PreparationLengthCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"


@admin.register(OrganizersNumberCategory)
class OrganizersNumberCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"


@admin.register(MaterialRequirementCategory)
class MaterialRequirementCategoryAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "description"
