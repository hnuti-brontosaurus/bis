from bis.admin_permissions import PermissionMixin
from cookbook_categories.models import (
    Allergen,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from django.contrib import admin
from nested_admin.nested import NestedModelAdmin


@admin.register(RecipeDifficulty)
class RecipeDifficultyAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(RecipeRequiredTime)
class RecipeRequiredTimeAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(RecipeTag)
class RecipeTagAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(Unit)
class UnitAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(Allergen)
class AllergenAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]
