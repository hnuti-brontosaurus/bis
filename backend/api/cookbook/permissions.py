from cookbook.models.menus import Menu
from cookbook.models.recipies import Recipe
from cookbook.models.units import Ingredient
from rest_framework.permissions import SAFE_METHODS, BasePermission


class CookbookAccessPermission(BasePermission):
    def has_cookbook_permission(self, request, view, obj=None):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False

        model = view.serializer_class.Meta.model

        if request.user.is_editor:
            return model in [Ingredient, Recipe, Menu]

        if model is Ingredient:
            return request.user.is_chef

        if model is Recipe:
            if not request.user.is_chef:
                return False
            if obj is None and request.method in ["POST", "PUT", "PATCH"]:
                return str(request.data.get("chef")) == str(request.user.chef.id)
            return obj is not None and obj.chef_id == request.user.chef.id

        if model is Menu:
            if obj is None and request.method in ["POST", "PUT", "PATCH"]:
                return str(request.data.get("user_id")) == str(request.user.id)
            return obj is not None and obj.user_id == request.user.id

        return False

    def has_permission(self, request, view):
        return self.has_cookbook_permission(request, view, None)

    def has_object_permission(self, request, view, obj):
        return self.has_cookbook_permission(request, view, obj)
