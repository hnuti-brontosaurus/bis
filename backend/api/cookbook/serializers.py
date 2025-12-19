from api.frontend.serializers import ModelSerializer
from cookbook.models.categories import RecipeDifficulty, RecipeTag
from cookbook.models.chefs import Chef
from cookbook.models.menus import Menu, MenuRecipe, MenuRecipeIngredient
from cookbook.models.recipies import (
    Recipe,
    RecipeComment,
    RecipeIngredient,
    RecipeStep,
    RecipeTip,
)
from cookbook.models.units import Ingredient, Unit


class RecipeDifficultySerializer(ModelSerializer):
    class Meta:
        model = RecipeDifficulty
        fields = ("id", "name", "slug", "order")


class RecipeTagSerializer(ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = ("id", "name", "slug", "order")


class ChefSerializer(ModelSerializer):
    class Meta:
        model = Chef
        fields = ("id", "user_id", "name", "email", "photo", "is_editor")


class UnitSerializer(ModelSerializer):
    class Meta:
        model = Unit
        fields = ("id", "name", "of")


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "state", "g_per_piece", "g_per_liter")


class RecipeIngredientSerializer(ModelSerializer):
    ingredient = IngredientSerializer()
    unit = UnitSerializer()

    class Meta:
        model = RecipeIngredient
        fields = (
            "order",
            "ingredient",
            "unit",
            "amount",
            "is_optional",
            "comment",
        )


class RecipeStepSerializer(ModelSerializer):
    class Meta:
        model = RecipeStep
        fields = (
            "name",
            "order",
            "is_optional",
            "description",
            "photo",
        )


class RecipeTipSerializer(ModelSerializer):
    class Meta:
        model = RecipeTip
        fields = ("name", "description")


class RecipeCommentSerializer(ModelSerializer):
    class Meta:
        model = RecipeComment
        fields = ("user_id", "created_at", "comment")
        read_only_fields = ("created_at",)


class RecipeSerializer(ModelSerializer):
    chef = ChefSerializer()
    difficulty = RecipeDifficultySerializer()
    tags = RecipeTagSerializer(many=True, required=False)

    ingredients = RecipeIngredientSerializer(many=True, required=False)
    steps = RecipeStepSerializer(many=True, required=False)
    tips = RecipeTipSerializer(many=True, required=False)
    comments = RecipeCommentSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "chef",
            "difficulty",
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
