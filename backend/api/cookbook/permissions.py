from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.menus import Menu
from cookbook.models.recipes import Recipe
from rest_framework.permissions import SAFE_METHODS, BasePermission


class CookbookAccessPermission(BasePermission):
    @staticmethod
    def match_id(request, obj, key, match):
        if obj:
            return str(getattr(obj, key)) == str(match)
        if key := request.data.get(key):
            return str(key) == str(match)
        return True

    def has_cookbook_permission(self, request, view, obj=None):
        model = view.serializer_class.Meta.model
        user = request.user

        if request.method in SAFE_METHODS:
            return True

        if view.action == "destroy":
            return False

        if not user or not user.is_authenticated:
            return False

        if user.is_editor:
            if model in [Ingredient, Recipe, Menu]:
                return True

        if model is Chef:
            return self.match_id(request, obj, "user_id", user.id)

        if not user.is_chef:
            return False

        if model is Ingredient:
            return True

        if model is Recipe:
            return self.match_id(request, obj, "chef_id", user.chef.id)

        return False

    def has_permission(self, request, view):
        return self.has_cookbook_permission(request, view, None)

    def has_object_permission(self, request, view, obj):
        return self.has_cookbook_permission(request, view, obj)
