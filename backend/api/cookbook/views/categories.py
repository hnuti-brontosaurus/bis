from rest_framework.viewsets import ModelViewSet

from api.cookbook.permissions import CookbookAccessPermission
from cookbook_categories.models import (
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from cookbook_categories.serializers import (
    RecipeDifficultySerializer,
    RecipeRequiredTimeSerializer,
    RecipeTagSerializer,
    UnitSerializer,
)


class RecipeDifficultyViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = RecipeDifficultySerializer
    queryset = RecipeDifficulty.objects.all()


class RecipeRequiredTimeViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = RecipeRequiredTimeSerializer
    queryset = RecipeRequiredTime.objects.all()


class RecipeTagViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = RecipeTagSerializer
    queryset = RecipeTag.objects.all()


class UnitViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()
