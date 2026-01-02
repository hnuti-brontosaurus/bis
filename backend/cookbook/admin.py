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
from django.contrib import admin
from nested_admin.nested import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline,
)


@admin.register(Chef)
class ChefAdmin(PermissionMixin, NestedModelAdmin):
    autocomplete_fields = ["user"]
    search_fields = ["name"]


class MenuRecipeIngredientAdmin(PermissionMixin, NestedTabularInline):
    model = MenuRecipeIngredient
    autocomplete_fields = ["ingredient", "unit"]


class MenuRecipeAdmin(PermissionMixin, NestedStackedInline):
    model = MenuRecipe
    inlines = [MenuRecipeIngredientAdmin]
    autocomplete_fields = ["original"]


@admin.register(Menu)
class MenuAdmin(PermissionMixin, NestedModelAdmin):
    inlines = [MenuRecipeAdmin]
    autocomplete_fields = ["user"]


class RecipeIngredientAdmin(PermissionMixin, NestedTabularInline):
    model = RecipeIngredient
    autocomplete_fields = ["ingredient", "unit"]


class RecipeStepAdmin(PermissionMixin, NestedTabularInline):
    model = RecipeStep
    pass


class RecipeTipAdmin(PermissionMixin, NestedTabularInline):
    model = RecipeTip
    pass


class RecipeCommentAdmin(PermissionMixin, NestedTabularInline):
    model = RecipeComment
    autocomplete_fields = ["user"]


@admin.register(Recipe)
class RecipeAdmin(PermissionMixin, NestedModelAdmin):
    inlines = [
        RecipeIngredientAdmin,
        RecipeStepAdmin,
        RecipeTipAdmin,
        RecipeCommentAdmin,
    ]
    autocomplete_fields = ["chef", "tags"]
    search_fields = ["name"]


@admin.register(Unit)
class UnitAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]


@admin.register(Ingredient)
class IngredientAdmin(PermissionMixin, NestedModelAdmin):
    search_fields = ["name"]
