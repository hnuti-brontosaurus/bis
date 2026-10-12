"""Cookbook serializers.

Field-shape rules:

- Non-owned FK / M2M relations (chef, difficulty, required_time, unit,
  ingredient, tags) expose ONLY the `_id` form on both read and write:
    chef_id      -> integer (FK)
    tag_ids      -> list[integer] (M2M)
    ingredient_id, unit_id -> integers on through rows
  No nested object is rendered for these — the frontend resolves names
  out of sibling stores keyed by id.

- Owned children of Recipe / Menu (ingredients, steps, tips, photos,
  menu_recipes, menu_recipe_ingredients) keep nested writes AND nested
  reads — they only exist as part of the parent and are rewritten via
  drf-writable-nested.

- Photo galleries are written in two ways: the recipe save keeps, reorders
  and deletes the existing photos through the nested `photos` lists, and
  each new photo is then POSTed on its own to a `*_photos` endpoint. One
  recipe save carrying every new photo as base64 is megabytes per photo and
  dies on the nginx timeout on slow networks; one request per photo can
  report progress and be retried alone.

- Model HTMLFields are written by chefs in the cookbook's rich-text editor
  and rendered as HTML, so they pass through `SanitizesHTML`, which keeps
  only what the editor can produce.
"""

import re
from itertools import groupby

import nh3
from cookbook.models.articles import Article, ArticleImage
from cookbook.models.cart import Cart
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.menus import Menu, MenuRecipe, MenuRecipeIngredient
from cookbook.models.recipes import (
    Recipe,
    RecipeComment,
    RecipeIngredient,
    RecipeIngredientPhoto,
    RecipePhoto,
    RecipeStep,
    RecipeStepPhoto,
    RecipeTip,
)
from cookbook_categories.models import (
    Allergen,
    IngredientCategory,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField, SlugRelatedField
from tinymce.models import HTMLField

BLANK = r"(?:\s|&nbsp;|\xa0|<br>)*"
IMAGE = re.compile(r'<img[^>]*\bsrc="([^"]*)"[^>]*>')


class SanitizedHTMLField(CharField):
    tags = {"p", "br", "strong", "em", "ul", "ol", "li", "a"}
    attributes = {"a": {"href"}}
    classes = {}

    def to_internal_value(self, data):
        html = nh3.clean(
            super().to_internal_value(data),
            tags=self.tags,
            attributes=self.attributes,
            allowed_classes=self.classes,
            set_tag_attribute_values={"a": {"target": "_blank"}},
        )
        html = re.sub(rf"(<(?:p|li|h2|h3)>){BLANK}", r"\1", html)
        html = re.sub(rf"{BLANK}(</(?:p|li|h2|h3)>)", r"\1", html)
        html = re.sub(r"<(p|li|h2|h3)></\1>", "", html)
        html = re.sub(r"<(ul|ol)></\1>", "", html)
        html = re.sub(rf"<br>{BLANK}<br>", "<br>", html).strip()
        if not html and not self.allow_blank:
            self.fail("blank")
        return html


class ArticleHTMLField(SanitizedHTMLField):
    tags = SanitizedHTMLField.tags | {"h2", "h3", "blockquote", "hr", "img"}
    attributes = {**SanitizedHTMLField.attributes, "img": {"src"}}
    classes = {
        "img": {"size-small-left", "size-small-right", "size-medium", "size-full"}
    }


class SanitizesHTML:
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        HTMLField: SanitizedHTMLField,
    }


class ChefSerializer(serializers.ModelSerializer):
    user_id = CharField()

    class Meta:
        model = Chef
        fields = ("id", "user_id", "name", "email", "photo", "is_editor")


class ArticleSerializer(serializers.ModelSerializer):
    content = ArticleHTMLField(allow_blank=True)

    class Meta:
        model = Article
        fields = ("slug", "content")
        read_only_fields = ("slug",)

    def update(self, instance, validated_data):
        """An image is uploaded on its own the moment it is inserted, see
        `ArticleImageSerializer`. The content is what decides which of them
        the article keeps: the rest are deleted, and an <img> that is not one
        of the article's images is dropped."""
        images = {image.src: image for image in instance.images.all()}
        kept = set()

        def keep(match):
            image = images.get(match[1])
            if image is None:
                return ""
            kept.add(image.id)
            return match[0]

        validated_data["content"] = IMAGE.sub(keep, validated_data["content"])
        instance = super().update(instance, validated_data)
        instance.images.exclude(id__in=kept).delete()
        return instance


class ArticleImageSerializer(serializers.ModelSerializer):
    article = SlugRelatedField(slug_field="slug", queryset=Article.objects.all())
    src = CharField(read_only=True)

    class Meta:
        model = ArticleImage
        fields = ("id", "article", "image", "src")
        extra_kwargs = {"image": {"write_only": True}}


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ("items", "other_items")


class IngredientSerializer(SanitizesHTML, serializers.ModelSerializer):
    allergen_ids = PrimaryKeyRelatedField(
        source="allergens",
        queryset=Allergen.objects.all(),
        many=True,
        required=False,
    )
    category_id = PrimaryKeyRelatedField(
        source="category",
        queryset=IngredientCategory.objects.all(),
        required=False,
    )

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "state",
            "g_per_piece",
            "g_per_liter",
            "g_per_serving",
            "category_id",
            "allergen_ids",
            "reasoning",
        )


class RecipePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipePhoto
        fields = ("id", "order", "photo")


class RecipeIngredientPhotoSerializer(RecipePhotoSerializer):
    class Meta(RecipePhotoSerializer.Meta):
        model = RecipeIngredientPhoto


class RecipeStepPhotoSerializer(RecipePhotoSerializer):
    class Meta(RecipePhotoSerializer.Meta):
        model = RecipeStepPhoto


class RecipePhotoUploadSerializer(RecipePhotoSerializer):
    parent_id = PrimaryKeyRelatedField(source="parent", queryset=Recipe.objects.all())

    class Meta(RecipePhotoSerializer.Meta):
        fields = (*RecipePhotoSerializer.Meta.fields, "parent_id")


class RecipeIngredientPhotoUploadSerializer(RecipeIngredientPhotoSerializer):
    parent_id = PrimaryKeyRelatedField(
        source="parent", queryset=RecipeIngredient.objects.all()
    )

    class Meta(RecipeIngredientPhotoSerializer.Meta):
        fields = (*RecipePhotoSerializer.Meta.fields, "parent_id")


class RecipeStepPhotoUploadSerializer(RecipeStepPhotoSerializer):
    parent_id = PrimaryKeyRelatedField(
        source="parent", queryset=RecipeStep.objects.all()
    )

    class Meta(RecipeStepPhotoSerializer.Meta):
        fields = (*RecipePhotoSerializer.Meta.fields, "parent_id")


class RecipeIngredientSerializer(SanitizesHTML, WritableNestedModelSerializer):
    ingredient_id = PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    unit_id = PrimaryKeyRelatedField(source="unit", queryset=Unit.objects.all())
    photos = RecipeIngredientPhotoSerializer(many=True, required=False)

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "order",
            "part",
            "ingredient_id",
            "unit_id",
            "amount",
            "is_optional",
            "comment",
            "photos",
        )


class RecipeStepSerializer(SanitizesHTML, WritableNestedModelSerializer):
    photos = RecipeStepPhotoSerializer(many=True, required=False)

    class Meta:
        model = RecipeStep
        fields = ("id", "name", "order", "description", "photos", "is_optional")


class RecipeTipSerializer(SanitizesHTML, serializers.ModelSerializer):
    class Meta:
        model = RecipeTip
        fields = ("id", "name", "description")


class RecipeCommentSerializer(SanitizesHTML, serializers.ModelSerializer):
    class Meta:
        model = RecipeComment
        fields = ("id", "user_id", "created_at", "comment")
        read_only_fields = ("created_at",)


class RecipeSerializer(SanitizesHTML, WritableNestedModelSerializer):
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
    photos = RecipePhotoSerializer(many=True, required=False)
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
            "photos",
            "intro",
            "sources",
            "default_servings",
            "servings_note",
            "difficulty_note",
            "ingredients",
            "steps",
            "tips",
            "comments",
            "allergen_ids",
            "is_public",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def validate_ingredients(self, ingredients):
        ordered = sorted(ingredients, key=lambda ingredient: ingredient["order"])
        parts = [part for part, _ in groupby(i.get("part", "") for i in ordered)]
        if len(parts) > 1 and "" in parts:
            raise serializers.ValidationError("Pojmenuj všechny části receptu.")
        if len(parts) != len(set(parts)):
            raise serializers.ValidationError(
                "Každá část receptu musí mít jiný název a být vcelku."
            )
        return ingredients

    def validate(self, attrs):
        # photos/intro/sources are required only when the recipe is public.
        # Need the *effective* post-write value, which on PATCH means
        # falling back to the current instance for fields not in `attrs`.
        def effective(field):
            if field in attrs:
                return attrs[field]
            if self.instance is None:
                return None
            if field == "photos":
                return self.instance.photos.exists()
            return getattr(self.instance, field)

        if effective("is_public"):
            errors = {}
            for field in ("photos", "intro", "sources"):
                if not effective(field):
                    errors[field] = "Veřejný recept musí mít vyplněné toto pole."
            if errors:
                raise serializers.ValidationError(errors)
        return super().validate(attrs)


class MenuRecipeIngredientSerializer(SanitizesHTML, serializers.ModelSerializer):
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


class MenuRecipeSerializer(SanitizesHTML, WritableNestedModelSerializer):
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


class MenuSerializer(SanitizesHTML, WritableNestedModelSerializer):
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
