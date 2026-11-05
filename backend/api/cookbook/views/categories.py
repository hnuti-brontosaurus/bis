from api.cookbook.permissions import CookbookViewSetMixin
from bis.cache import CachedViewSetMixin, invalidate_cache
from cookbook_categories.models import (
    Allergen,
    IngredientCategory,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from cookbook_categories.serializers import (
    AllergenSerializer,
    IngredientCategorySerializer,
    RecipeDifficultySerializer,
    RecipeRequiredTimeSerializer,
    RecipeTagSerializer,
    UnitSerializer,
)
from rest_framework.mixins import CreateModelMixin
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


class RecipeTagViewSet(
    CookbookViewSetMixin, CreateModelMixin, CachedCookbookCategoryViewSet
):
    serializer_class = RecipeTagSerializer
    queryset = RecipeTag.objects.all()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_cache(self.cache_namespace)


class UnitViewSet(CachedCookbookCategoryViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()


class AllergenViewSet(CachedCookbookCategoryViewSet):
    serializer_class = AllergenSerializer
    queryset = Allergen.objects.all()


class IngredientCategoryViewSet(CachedCookbookCategoryViewSet):
    serializer_class = IngredientCategorySerializer
    queryset = IngredientCategory.objects.all()
