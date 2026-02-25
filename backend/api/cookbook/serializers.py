from rest_framework.fields import CharField, FloatField

from api.frontend.serializers import (
    ModelSerializer,
    SmartUpdatableListSerializer,
    UpdatableListSerializer,
)
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.menus import Menu, MenuRecipe, MenuRecipeIngredient
from cookbook.models.recipes import (
    Recipe,
    RecipeComment,
    RecipeIngredient,
    RecipeStep,
    RecipeTip,
)
from cookbook_categories.serializers import (
    RecipeDifficultySerializer,
    RecipeRequiredTimeSerializer,
    RecipeTagSerializer,
    UnitSerializer,
)


class ChefSerializer(ModelSerializer):
    user_id = CharField()

    class Meta:
        model = Chef
        fields = ("id", "user_id", "name", "email", "photo", "is_editor")


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "state", "g_per_piece", "g_per_liter")


class RecipeIngredientSerializer(ModelSerializer):
    ingredient = IngredientSerializer()
    unit = UnitSerializer()

    class Meta:
        nested = True
        model = RecipeIngredient
        fields = (
            "id",
            "order",
            "ingredient",
            "unit",
            "amount",
            "is_required",
            "comment",
        )
        list_serializer_class = SmartUpdatableListSerializer


class RecipeStepSerializer(ModelSerializer):
    class Meta:
        nested = True
        model = RecipeStep
        fields = (
            "id",
            "name",
            "order",
            "description",
            "photo",
        )
        list_serializer_class = SmartUpdatableListSerializer


class RecipeTipSerializer(ModelSerializer):
    class Meta:
        nested = True
        model = RecipeTip
        fields = ("id", "name", "description")
        list_serializer_class = SmartUpdatableListSerializer


class RecipeCommentSerializer(ModelSerializer):
    class Meta:
        model = RecipeComment
        fields = ("id", "user_id", "created_at", "comment")
        read_only_fields = ("created_at",)


class RecipeSerializer(ModelSerializer):
    chef = ChefSerializer()
    difficulty = RecipeDifficultySerializer()
    required_time = RecipeRequiredTimeSerializer()
    tags = RecipeTagSerializer(many=True, required=False)

    ingredients = RecipeIngredientSerializer(many=True, required=False)
    steps = RecipeStepSerializer(many=True, required=False)
    tips = RecipeTipSerializer(many=True, required=False)
    comments = RecipeCommentSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        read_only_fields = ("comments",)
        fields = (
            "id",
            "name",
            "chef",
            "difficulty",
            "required_time",
            "tags",
            "photo",
            "intro",
            "sources",
            "ingredients",
            "steps",
            "tips",
            "comments",
            "is_public",
        )


class RecipeReferenceSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "photo")


class MenuRecipeIngredientSerializer(ModelSerializer):
    ingredient = IngredientSerializer()
    unit = UnitSerializer()

    class Meta:
        model = MenuRecipeIngredient
        fields = (
            "id",
            "ingredient",
            "unit",
            "amount",
            "is_used",
            "comment",
        )


class MenuRecipeSerializer(ModelSerializer):
    original = RecipeReferenceSerializer(allow_null=True)
    menu_recipe_ingredients = MenuRecipeIngredientSerializer(many=True, required=False)

    class Meta:
        model = MenuRecipe
        fields = (
            "id",
            "name",
            "original",
            "note",
            "served_at",
            "menu_recipe_ingredients",
        )


class MenuSerializer(ModelSerializer):
    menu_recipes = MenuRecipeSerializer(many=True, required=False)

    class Meta:
        model = Menu
        fields = (
            "id",
            "name",
            "description",
            "user_id",
            "is_shared",
            "is_starred",
            "menu_recipes",
        )
