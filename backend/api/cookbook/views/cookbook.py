from api.cookbook.filters import MenuFilter, RecipeFilter
from api.cookbook.permissions import CookbookAccessPermission
from api.cookbook.serializers import (
    ChefSerializer,
    IngredientSerializer,
    MenuSerializer,
    RecipeSerializer,
)
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.menus import Menu
from cookbook.models.recipes import Recipe
from rest_framework.viewsets import ModelViewSet


class ChangeViewSetMixin:
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class RecipeViewSet(ChangeViewSetMixin, ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter
    queryset = (
        Recipe.objects.select_related("chef", "chef__user", "difficulty")
        .prefetch_related(
            "tags",
            "ingredients",
            "ingredients__ingredient",
            "ingredients__unit",
            "steps",
            "tips",
            "comments",
            "comments__user",
        )
        .all()
    )


class MenuViewSet(ChangeViewSetMixin, ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
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


class ChefViewSet(ChangeViewSetMixin, ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name", "user__first_name", "user__last_name"]
    serializer_class = ChefSerializer
    queryset = Chef.objects.select_related("user").all()


class IngredientViewSet(ChangeViewSetMixin, ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
