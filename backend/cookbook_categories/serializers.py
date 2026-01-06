from api.frontend.serializers import ModelSerializer
from cookbook_categories.models import (
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)


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
    class Meta:
        model = RecipeTag
        exclude = ()


class UnitSerializer(BaseCategorySerializer):
    class Meta:
        model = Unit
        exclude = ()
