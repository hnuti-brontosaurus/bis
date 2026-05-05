"""Cookbook serializers.

Field-shape rules:

- Non-owned FK / M2M relations (chef, difficulty, required_time, unit,
  ingredient, tags) expose ONLY the `_id` form on both read and write:
    chef_id      -> integer (FK)
    tag_ids      -> list[integer] (M2M)
    ingredient_id, unit_id -> integers on through rows
  No nested object is rendered for these — the frontend resolves names
  out of sibling stores keyed by id.

- Owned children of Recipe / Menu (ingredients, steps, tips,
  menu_recipes, menu_recipe_ingredients) keep nested writes AND nested
  reads — they only exist as part of the parent and are rewritten via
  drf-writable-nested.
"""

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
    Allergen,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField


class ChefSerializer(serializers.ModelSerializer):
    user_id = CharField()

    class Meta:
        model = Chef
        fields = ("id", "user_id", "name", "email", "photo", "is_editor")


class IngredientSerializer(serializers.ModelSerializer):
    allergen_ids = PrimaryKeyRelatedField(
        source="allergens",
        queryset=Allergen.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Ingredient
        fields = ("id", "name", "state", "g_per_piece", "g_per_liter", "allergen_ids")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_id = PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    unit_id = PrimaryKeyRelatedField(source="unit", queryset=Unit.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "order",
            "ingredient_id",
            "unit_id",
            "amount",
            "is_required",
            "comment",
        )


class RecipeStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeStep
        fields = ("id", "name", "order", "description", "photo")


class RecipeTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTip
        fields = ("id", "name", "description")


class RecipeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeComment
        fields = ("id", "user_id", "created_at", "comment")
        read_only_fields = ("created_at",)


class RecipeSerializer(WritableNestedModelSerializer):
    chef_id = PrimaryKeyRelatedField(source="chef", queryset=Chef.objects.all())
    difficulty_id = PrimaryKeyRelatedField(
        source="difficulty", queryset=RecipeDifficulty.objects.all()
    )
    required_time_id = PrimaryKeyRelatedField(
        source="required_time", queryset=RecipeRequiredTime.objects.all()
    )
    tag_ids = PrimaryKeyRelatedField(
        source="tags",
        queryset=RecipeTag.objects.all(),
        many=True,
        required=False,
    )

    ingredients = RecipeIngredientSerializer(many=True, required=False)
    steps = RecipeStepSerializer(many=True, required=False)
    tips = RecipeTipSerializer(many=True, required=False)
    comments = RecipeCommentSerializer(many=True, required=False, read_only=True)
    # Cached on the Recipe via signals (cookbook.signals); chefs edit
    # allergens on the Ingredient, never per-recipe.
    allergen_ids = PrimaryKeyRelatedField(source="allergens", many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "chef_id",
            "difficulty_id",
            "required_time_id",
            "tag_ids",
            "photo",
            "intro",
            "sources",
            "ingredients",
            "steps",
            "tips",
            "comments",
            "allergen_ids",
            "is_public",
        )

    def validate(self, attrs):
        # photo/intro/sources are required only when the recipe is public.
        # Need the *effective* post-write value, which on PATCH means
        # falling back to the current instance for fields not in `attrs`.
        def effective(field):
            if field in attrs:
                return attrs[field]
            return getattr(self.instance, field, None)

        if effective("is_public"):
            errors = {}
            for field in ("photo", "intro", "sources"):
                if not effective(field):
                    errors[field] = "Veřejný recept musí mít vyplněné toto pole."
            if errors:
                raise serializers.ValidationError(errors)
        return super().validate(attrs)


class RecipeReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "photo")


class MenuRecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_id = PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    unit_id = PrimaryKeyRelatedField(source="unit", queryset=Unit.objects.all())

    class Meta:
        model = MenuRecipeIngredient
        fields = (
            "id",
            "ingredient_id",
            "unit_id",
            "amount",
            "is_used",
            "comment",
        )


class MenuRecipeSerializer(WritableNestedModelSerializer):
    original_id = PrimaryKeyRelatedField(
        source="original",
        queryset=Recipe.objects.all(),
        allow_null=True,
        required=False,
    )
    menu_recipe_ingredients = MenuRecipeIngredientSerializer(many=True, required=False)

    class Meta:
        model = MenuRecipe
        fields = (
            "id",
            "name",
            "original_id",
            "note",
            "served_at",
            "menu_recipe_ingredients",
        )


class MenuSerializer(WritableNestedModelSerializer):
    menu_recipes = MenuRecipeSerializer(many=True, required=False)

    class Meta:
        model = Menu
        fields = (
            "id",
            "name",
            "description",
            "user_id",
            "is_shared",
            "is_starred",
            "menu_recipes",
        )
