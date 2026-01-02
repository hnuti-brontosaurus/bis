from api.cookbook.permissions import CookbookAccessPermission
from cookbook_categories.models import RecipeDifficulty, RecipeTag
from cookbook_categories.serializers import (
    RecipeDifficultySerializer,
    RecipeTagSerializer,
)
from rest_framework.viewsets import ModelViewSet


class RecipeDifficultyViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = RecipeDifficultySerializer
    queryset = RecipeDifficulty.objects.all()


class RecipeTagViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = RecipeTagSerializer
    queryset = RecipeTag.objects.all()
