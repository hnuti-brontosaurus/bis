from api.cookbook.views import (
    ChefViewSet,
    IngredientViewSet,
    MenuViewSet,
    RecipeDifficultyViewSet,
    RecipeTagViewSet,
    RecipeViewSet,
    UnitViewSet,
)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

router.register("recipes", RecipeViewSet, "recipes")
router.register("menus", MenuViewSet, "menus")
router.register("chefs", ChefViewSet, "chefs")
router.register("units", UnitViewSet, "units")
router.register("ingredients", IngredientViewSet, "ingredients")
router.register("recipe_difficulties", RecipeDifficultyViewSet, "recipe_difficulties")
router.register("recipe_tags", RecipeTagViewSet, "recipe_tags")

urlpatterns = [path("", include(router.urls))]
