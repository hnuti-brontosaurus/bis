from api.cookbook.filters import MenuFilter, RecipeFilter
from api.cookbook.permissions import CookbookViewSetMixin
from api.cookbook.serializers import (
    ArticleImageSerializer,
    ArticleSerializer,
    ChefSerializer,
    IngredientSerializer,
    MenuSerializer,
    RecipeIngredientPhotoUploadSerializer,
    RecipePhotoUploadSerializer,
    RecipeSerializer,
    RecipeStepPhotoUploadSerializer,
)
from cookbook.models.articles import Article, ArticleImage
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.menus import Menu
from cookbook.models.recipes import (
    Recipe,
    RecipeIngredientPhoto,
    RecipePhoto,
    RecipeStepPhoto,
)
from cookbook.services.ingredient_enrichment import enrich_ingredient
from django.http import Http404
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
            "photos",
            "ingredients__photos",
            "steps__photos",
            "tips",
            "comments",
            "comments__user",
        )
        .all()
    )


class PhotoUploadViewSet(
    CookbookViewSetMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """POST-only: adds one photo to a gallery, see the photo notes in
    `api/cookbook/serializers.py`. Photos are deleted and reordered by the
    recipe save."""

    http_method_names = ["post", "options", "head"]


class RecipePhotoViewSet(PhotoUploadViewSet):
    serializer_class = RecipePhotoUploadSerializer
    queryset = RecipePhoto.objects.all()


class RecipeIngredientPhotoViewSet(PhotoUploadViewSet):
    serializer_class = RecipeIngredientPhotoUploadSerializer
    queryset = RecipeIngredientPhoto.objects.all()


class RecipeStepPhotoViewSet(PhotoUploadViewSet):
    serializer_class = RecipeStepPhotoUploadSerializer
    queryset = RecipeStepPhoto.objects.all()


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


class ArticleViewSet(
    CookbookViewSetMixin,
    ChangeViewSetMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """The set of articles is fixed by `Article.Slug`, so a row is created
    the first time its slug is looked up instead of being seeded — a seed
    would not survive `testing_db dev`, which flushes the database."""

    lookup_field = "slug"
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def get_object(self):
        slug = self.kwargs["slug"]
        if slug not in Article.Slug.values:
            raise Http404
        article, _ = Article.objects.get_or_create(slug=slug)
        self.check_object_permissions(self.request, article)
        return article


class ArticleImageViewSet(
    CookbookViewSetMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    http_method_names = ["post", "options", "head"]
    serializer_class = ArticleImageSerializer
    queryset = ArticleImage.objects.all()
