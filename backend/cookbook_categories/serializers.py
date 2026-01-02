from api.frontend.serializers import ModelSerializer
from cookbook_categories.models import RecipeDifficulty, RecipeTag


class RecipeDifficultySerializer(ModelSerializer):
    class Meta:
        model = RecipeDifficulty
        exclude = ()


class RecipeTagSerializer(ModelSerializer):
    class Meta:
        model = RecipeTag
        exclude = ()
