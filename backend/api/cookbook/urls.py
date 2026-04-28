import api.cookbook.views.auth
import api.cookbook.views.extras
from api.cookbook.views.categories import (
    RecipeDifficultyViewSet,
    RecipeRequiredTimeViewSet,
    RecipeTagViewSet,
    UnitViewSet,
)
from api.cookbook.views.cookbook import (
    ChefViewSet,
    IngredientViewSet,
    MenuViewSet,
    RecipeViewSet,
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
router.register(
    "recipe_required_times", RecipeRequiredTimeViewSet, "recipe_required_times"
)
router.register("recipe_tags", RecipeTagViewSet, "recipe_tags")

urlpatterns = [
    path("", include(router.urls)),
    path("extras/translations/", api.cookbook.views.extras.translations),
    path("auth/whoami/", api.cookbook.views.auth.whoami),
    path("auth/check_email/", api.cookbook.views.auth.check_email),
    path("auth/validate_password/", api.cookbook.views.auth.check_password),
    path("auth/register/", api.cookbook.views.auth.register),
    path("auth/login/", api.cookbook.views.auth.login),
]
