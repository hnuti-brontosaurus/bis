import django_filters

from cookbook.models.menus import Menu
from cookbook.models.recipes import Recipe


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class RecipeFilter(django_filters.FilterSet):
    id = NumberInFilter()
    chef = NumberInFilter(field_name="chef_id")
    difficulty = NumberInFilter(field_name="difficulty_id")
    tags = NumberInFilter(field_name="tags")

    class Meta:
        model = Recipe
        fields = []


class MenuFilter(django_filters.FilterSet):
    id = NumberInFilter()
    user = NumberInFilter(field_name="user_id")

    class Meta:
        model = Menu
        fields = []
