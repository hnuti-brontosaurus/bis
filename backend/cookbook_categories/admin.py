from bis.admin_permissions import PermissionMixin
from cookbook.models.chefs import Chef
from cookbook.models.menus import Menu, MenuRecipe, MenuRecipeIngredient
from cookbook.models.recipies import (
    Recipe,
    RecipeComment,
    RecipeIngredient,
    RecipeStep,
    RecipeTip,
)
from cookbook.models.units import Ingredient, Unit
from cookbook_categories.models import (
    RecipeCourse,
    RecipeDietRestriction,
    RecipeDifficulty,
    RecipeTag,
    RecipeTimeRequired,
    RecipeType,
)
from django.contrib import admin
from nested_admin.nested import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline,
)


@admin.register(RecipeDifficulty)
class RecipeDifficultyAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(RecipeTimeRequired)
class RecipeTimeRequiredAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(RecipeDietRestriction)
class RecipeDietRestrictionAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(RecipeCourse)
class RecipeCourseAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(RecipeType)
class RecipeTypeAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(RecipeTag)
class RecipeTagAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]
