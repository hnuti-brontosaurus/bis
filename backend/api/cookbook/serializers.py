"""Cookbook serializers.

Field-shape rules:

- Non-owned FK / M2M relations (chef, difficulty, required_time, unit,
  ingredient, tags) expose ONLY the `_id` form on both read and write:
    chef_id      -> integer (FK)
    tag_ids      -> list[integer] (M2M)
    ingredient_id, unit_id -> integers on through rows
  No nested object is rendered for these — the frontend resolves names
  out of sibling stores keyed by id.

- Owned children of Recipe (ingredients, steps, tips) keep nested writes
  AND nested reads — they only exist as part of the parent recipe and
  the parent serializer rewrites them on PATCH/POST via NestedParentMixin.
"""

from api.frontend.serializers import SmartUpdatableListSerializer
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
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ManyToManyField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.utils import model_meta


class NestedParentMixin:
    """Adds nested-child create/update for owned reverse relations.

    Children declared as nested ModelSerializer fields (with `Meta.nested =
    True`) are extracted from validated_data and rewritten via the child
    serializer using SmartUpdatableListSerializer semantics.
    """

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except DjangoValidationError as e:
            raise ValidationError(e.messages) from e

    @property
    def _nested_child_fields(self):
        """Map of field_name -> (child_serializer_class, reverse_fk_name)."""
        result = {}
        for field_name, field in self.fields.items():
            inner = (
                field.child if isinstance(field, serializers.ListSerializer) else field
            )
            if isinstance(inner, serializers.ModelSerializer) and getattr(
                inner.Meta, "nested", False
            ):
                reverse = self.Meta.model._meta.get_field(field_name).remote_field.name
                result[field_name] = (type(inner), reverse)
        return result

    @property
    def _m2m_field_names(self):
        info = model_meta.get_field_info(self.Meta.model)
        return [
            name
            for name, rel in info.relations.items()
            if isinstance(rel.model_field, ManyToManyField)
        ]

    @staticmethod
    def _pop_keys(data, keys):
        return {k: data.pop(k) for k in keys if k in data}

    @transaction.atomic
    def create(self, validated_data):
        nested = self._pop_keys(validated_data, self._nested_child_fields.keys())
        m2m = self._pop_keys(validated_data, self._m2m_field_names)
        instance = self.Meta.model.objects.create(**validated_data)
        self._write_nested(instance, nested)
        for name, value in m2m.items():
            getattr(instance, name).set(value)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        nested = self._pop_keys(validated_data, self._nested_child_fields.keys())
        m2m = self._pop_keys(validated_data, self._m2m_field_names)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._write_nested(instance, nested)
        for name, value in m2m.items():
            getattr(instance, name).set(value)
        return instance

    def _write_nested(self, instance, nested_data):
        for field_name, value in nested_data.items():
            child_class, reverse = self._nested_child_fields[field_name]
            current = getattr(instance, field_name, None)
            if value is None:
                if current is not None and hasattr(current, "delete"):
                    current.delete()
                continue
            child = child_class(
                instance=current,
                data=self.initial_data[field_name],
                context=self.context,
                many=isinstance(value, list),
            )
            child.is_valid(raise_exception=True)
            child.save(**{reverse: instance})


class ChefSerializer(serializers.ModelSerializer):
    user_id = CharField()

    class Meta:
        model = Chef
        fields = ("id", "user_id", "name", "email", "photo", "is_editor")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "state", "g_per_piece", "g_per_liter")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_id = PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    unit_id = PrimaryKeyRelatedField(source="unit", queryset=Unit.objects.all())

    class Meta:
        nested = True
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
        list_serializer_class = SmartUpdatableListSerializer


class RecipeStepSerializer(serializers.ModelSerializer):
    class Meta:
        nested = True
        model = RecipeStep
        fields = ("id", "name", "order", "description", "photo")
        list_serializer_class = SmartUpdatableListSerializer


class RecipeTipSerializer(serializers.ModelSerializer):
    class Meta:
        nested = True
        model = RecipeTip
        fields = ("id", "name", "description")
        list_serializer_class = SmartUpdatableListSerializer


class RecipeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeComment
        fields = ("id", "user_id", "created_at", "comment")
        read_only_fields = ("created_at",)


class RecipeSerializer(NestedParentMixin, serializers.ModelSerializer):
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
            "is_public",
        )


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
        nested = True
        model = MenuRecipeIngredient
        fields = (
            "id",
            "ingredient_id",
            "unit_id",
            "amount",
            "is_used",
            "comment",
        )
        list_serializer_class = SmartUpdatableListSerializer


class MenuRecipeSerializer(NestedParentMixin, serializers.ModelSerializer):
    original_id = PrimaryKeyRelatedField(
        source="original",
        queryset=Recipe.objects.all(),
        allow_null=True,
        required=False,
    )
    menu_recipe_ingredients = MenuRecipeIngredientSerializer(many=True, required=False)

    class Meta:
        nested = True
        model = MenuRecipe
        fields = (
            "id",
            "name",
            "original_id",
            "note",
            "served_at",
            "menu_recipe_ingredients",
        )
        list_serializer_class = SmartUpdatableListSerializer


class MenuSerializer(NestedParentMixin, serializers.ModelSerializer):
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
