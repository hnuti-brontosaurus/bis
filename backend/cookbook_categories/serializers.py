from api.frontend.serializers import ModelSerializer
from cookbook_categories.models import (
    Allergen,
    IngredientCategory,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from django.db.models import Max
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class BaseCategorySerializer(ModelSerializer):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Globally excluded fields
        excluded_fields = [
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

        for field_name in excluded_fields:
            if field_name in self.fields:
                self.fields.pop(field_name)


class RecipeDifficultySerializer(BaseCategorySerializer):
    class Meta:
        model = RecipeDifficulty
        exclude = ()


class RecipeRequiredTimeSerializer(BaseCategorySerializer):
    class Meta:
        model = RecipeRequiredTime
        exclude = ()


class RecipeTagSerializer(BaseCategorySerializer):
    """Editors add tags to the existing groups only; groups, renames and
    reordering stay in the admin."""

    class Meta:
        model = RecipeTag
        exclude = ()
        read_only_fields = ("slug", "order")

    def validate_group(self, group):
        if not RecipeTag.objects.filter(group=group).exists():
            raise ValidationError("Neznámá kategorie tagů.")
        return group

    def validate(self, attrs):
        if RecipeTag.objects.filter(
            group=attrs["group"], name__iexact=attrs["name"]
        ).exists():
            raise ValidationError({"name": "Tento tag už v kategorii je."})
        return attrs

    def create(self, validated_data):
        base = slugify(validated_data["name"]) or "tag"
        slug, suffix = base, 1
        while RecipeTag.objects.filter(slug=slug).exists():
            suffix += 1
            slug = f"{base}-{suffix}"
        last = RecipeTag.objects.filter(group=validated_data["group"]).aggregate(
            order=Max("order")
        )["order"]
        return super().create({**validated_data, "slug": slug, "order": last + 1})


class UnitSerializer(BaseCategorySerializer):
    class Meta:
        model = Unit
        exclude = ()


class AllergenSerializer(BaseCategorySerializer):
    class Meta:
        model = Allergen
        exclude = ()


class IngredientCategorySerializer(BaseCategorySerializer):
    class Meta:
        model = IngredientCategory
        exclude = ()
