from bis.cache import CachedViewSetMixin
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
from rest_framework.viewsets import ReadOnlyModelViewSet


class CachedCookbookCategoryViewSet(CachedViewSetMixin, ReadOnlyModelViewSet):
    cache_namespace = "cookbook_categories"
    lookup_field = "id"
    search_fields = ["name"]


class RecipeDifficultyViewSet(CachedCookbookCategoryViewSet):
    serializer_class = RecipeDifficultySerializer
    queryset = RecipeDifficulty.objects.all()


class RecipeRequiredTimeViewSet(CachedCookbookCategoryViewSet):
    serializer_class = RecipeRequiredTimeSerializer
    queryset = RecipeRequiredTime.objects.all()


class RecipeTagViewSet(CachedCookbookCategoryViewSet):
    serializer_class = RecipeTagSerializer
    queryset = RecipeTag.objects.all()


class UnitViewSet(CachedCookbookCategoryViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()


class AllergenViewSet(CachedCookbookCategoryViewSet):
    serializer_class = AllergenSerializer
    queryset = Allergen.objects.all()
