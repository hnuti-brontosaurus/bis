from django.contrib import admin
from nested_admin.nested import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline,
)

from bis.admin_permissions import PermissionMixin
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.menus import Menu, MenuRecipe, MenuRecipeIngredient
from cookbook.models.recipes import (
    Recipe,
    RecipeComment,
    RecipeIngredient,
    RecipeStep,
    RecipeTip,
)
from cookbook_categories.models import (
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)


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
