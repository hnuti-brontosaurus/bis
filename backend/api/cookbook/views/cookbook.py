from api.cookbook.filters import MenuFilter, RecipeFilter
from api.cookbook.permissions import CookbookViewSetMixin
from api.cookbook.serializers import (
    ChefSerializer,
    IngredientSerializer,
    MenuSerializer,
    RecipeSerializer,
    RecipeStepPhotoSerializer,
)
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.menus import Menu
from cookbook.models.recipes import Recipe, RecipeStep
from cookbook.services.ingredient_enrichment import enrich_ingredient
from rest_framework import mixins, viewsets
from rest_framework.viewsets import ModelViewSet


class ChangeViewSetMixin:
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class RecipeViewSet(CookbookViewSetMixin, ChangeViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name"]
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter
    queryset = (
        Recipe.objects.select_related("chef", "chef__user", "difficulty")
        .prefetch_related(
            "tags",
            "allergens",
            "ingredients",
            "steps",
            "tips",
            "comments",
            "comments__user",
        )
        .all()
    )


class RecipeStepViewSet(
    CookbookViewSetMixin,
    ChangeViewSetMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """PATCH-only endpoint for uploading a single step's photo.

    The frontend uses this to stream step photos one-by-one (with progress
    + retry) instead of bundling them into the recipe PATCH.
    """

    lookup_field = "id"
    serializer_class = RecipeStepPhotoSerializer
    queryset = RecipeStep.objects.select_related("recipe").all()
    http_method_names = ["patch", "options", "head"]


class MenuViewSet(CookbookViewSetMixin, ChangeViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name"]
    serializer_class = MenuSerializer
    filterset_class = MenuFilter
    queryset = (
        Menu.objects.select_related("user")
        .prefetch_related(
            "menu_recipes",
            "menu_recipes__original",
            "menu_recipes__menu_recipe_ingredients",
            "menu_recipes__menu_recipe_ingredients__ingredient",
            "menu_recipes__menu_recipe_ingredients__unit",
        )
        .all()
    )


class ChefViewSet(CookbookViewSetMixin, ChangeViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name", "user__first_name", "user__last_name"]
    serializer_class = ChefSerializer
    queryset = Chef.objects.select_related("user").all()


class IngredientViewSet(CookbookViewSetMixin, ChangeViewSetMixin, ModelViewSet):
    lookup_field = "id"
    search_fields = ["name"]
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        if enrich_ingredient(instance):
            instance.save()
