import api.cookbook.views.auth
from api.cookbook.views.categories import RecipeDifficultyViewSet, RecipeTagViewSet
from api.cookbook.views.cookbook import (
    ChefViewSet,
    IngredientViewSet,
    MenuViewSet,
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

urlpatterns = [
    path("", include(router.urls)),
    # path("auth/whoami/", api.cookbook.views.auth.whoami),
    # path("auth/login/", api.cookbook.views.auth.whoami),
    # path("auth/send_verification_link/", api.cookbook.views.auth.whoami),
    # path("auth/register/", api.cookbook.views.auth.register),
    # path("auth/logout/", api.cookbook.views.auth.logout),
]
