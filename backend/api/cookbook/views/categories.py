from api.cookbook.permissions import CookbookViewSetMixin
from cookbook_categories.models import (
    Allergen,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from cookbook_categories.serializers import (
    AllergenSerializer,
    RecipeDifficultySerializer,
    RecipeRequiredTimeSerializer,
    RecipeTagSerializer,
    UnitSerializer,
)
from rest_framework.viewsets import ModelViewSet


class RecipeDifficultyViewSet(CookbookViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name"]
    serializer_class = RecipeDifficultySerializer
    queryset = RecipeDifficulty.objects.all()


class RecipeRequiredTimeViewSet(CookbookViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name"]
    serializer_class = RecipeRequiredTimeSerializer
    queryset = RecipeRequiredTime.objects.all()


class RecipeTagViewSet(CookbookViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name"]
    serializer_class = RecipeTagSerializer
    queryset = RecipeTag.objects.all()


class UnitViewSet(CookbookViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name"]
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()


class AllergenViewSet(CookbookViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name"]
    serializer_class = AllergenSerializer
    queryset = Allergen.objects.all()
