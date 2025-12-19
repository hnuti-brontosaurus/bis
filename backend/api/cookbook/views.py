from api.cookbook.filters import MenuFilter, RecipeFilter
from api.cookbook.permissions import CookbookAccessPermission
from api.cookbook.serializers import (
    ChefSerializer,
    IngredientSerializer,
    MenuSerializer,
    RecipeDifficultySerializer,
    RecipeSerializer,
    RecipeTagSerializer,
    UnitSerializer,
)
from cookbook.models.categories import RecipeDifficulty, RecipeTag
from cookbook.models.chefs import Chef
from cookbook.models.menus import Menu
from cookbook.models.recipies import Recipe
from cookbook.models.units import Ingredient, Unit
from rest_framework.viewsets import ModelViewSet


class RecipeViewSet(ModelViewSet):
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


class MenuViewSet(ModelViewSet):
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


class ChefViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name", "user__first_name", "user__last_name"]
    serializer_class = ChefSerializer
    queryset = Chef.objects.select_related("user").all()


class UnitViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()


class IngredientViewSet(ModelViewSet):
    lookup_field = "id"
    permission_classes = [CookbookAccessPermission]
    search_fields = ["name"]
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
