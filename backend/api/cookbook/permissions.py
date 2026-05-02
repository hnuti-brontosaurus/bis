"""Cookbook access rules — visibility and write permissions in one place.

Visibility (reads / list filtering):
  * Ingredient: visible to everyone.
  * Chef: editors see all; everyone else sees only chefs with at least one
    `is_public` recipe, plus the viewer's own chef row.
  * Recipe: editors see all; chefs see is_public + own; others see is_public.
  * Menu:   editors see all; chefs see is_shared + own; others see is_shared.

Writes:
  * Chef: a user creates / edits only their own chef row; never deletes.
  * Ingredient: any chef can create / edit / delete. The DB PROTECTs deletion
    of ingredients still referenced by a recipe.
  * Recipe: chef creates / edits / deletes own; editor edits / deletes any.
  * Menu: chef creates / edits / deletes own; editor edits / deletes any.

The viewset wires this in via `CookbookViewSetMixin`, which both sets
`permission_classes` and applies `filter_visible` in `get_queryset`.
"""

from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.menus import Menu
from cookbook.models.recipes import Recipe
from cookbook_categories.models import (
    Allergen,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission


class CookbookAccessPermission(BasePermission):
    @staticmethod
    def _matches(request, obj, field, expected):
        if obj is not None:
            return getattr(obj, field) == expected
        value = request.data.get(field)
        return value is not None and str(value) == str(expected)

    @classmethod
    def filter_visible(cls, request, queryset):
        model = queryset.model
        user = request.user

        if model in (
            Ingredient,
            Allergen,
            RecipeDifficulty,
            RecipeRequiredTime,
            RecipeTag,
            Unit,
        ):
            return queryset

        if user.is_authenticated and user.is_editor:
            return queryset

        if model is Chef:
            # Show chefs with at least one recipe the viewer can see, plus
            # the viewer's own chef row. Non-chefs only see "public-author"
            # chefs.
            visible_authors = Chef.objects.filter(recipes__is_public=True)
            if user.is_authenticated and user.is_chef:
                return queryset.filter(Q(id__in=visible_authors) | Q(id=user.chef.id))
            return queryset.filter(id__in=visible_authors)

        if model is Recipe:
            if user.is_authenticated and user.is_chef:
                return queryset.filter(Q(is_public=True) | Q(chef_id=user.chef.id))
            return queryset.filter(is_public=True)

        if model is Menu:
            if user.is_authenticated and user.is_chef:
                return queryset.filter(Q(is_shared=True) | Q(user_id=user.id))
            return queryset.filter(is_shared=True)

        return queryset.none()

    def _can_read(self, request, obj):
        model = type(obj)
        user = request.user

        if model is Recipe:
            if obj.is_public:
                return True
            if user.is_authenticated and user.is_editor:
                return True
            return (
                user.is_authenticated and user.is_chef and obj.chef_id == user.chef.id
            )

        if model is Menu:
            if obj.is_shared:
                return True
            if user.is_authenticated and user.is_editor:
                return True
            return user.is_authenticated and obj.user_id == user.id

        if model is Chef:
            if user.is_authenticated and user.is_editor:
                return True
            if user.is_authenticated and user.is_chef and obj.id == user.chef.id:
                return True
            return obj.recipes.filter(is_public=True).exists()

        # Ingredient and category models are world-readable.
        return True

    def _can_write(self, request, view, obj):
        model = view.serializer_class.Meta.model
        user = request.user
        action = view.action

        if not user or not user.is_authenticated:
            return False

        if model is Chef:
            if action == "destroy":
                return False
            return self._matches(request, obj, "user_id", user.id)

        if not user.is_chef:
            return False

        if model is Ingredient:
            return True

        if user.is_editor:
            return model in (Recipe, Menu)

        if model is Recipe:
            return self._matches(request, obj, "chef_id", user.chef.id)

        if model is Menu:
            return self._matches(request, obj, "user_id", user.id)

        return False

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if view.action == "create":
            return self._can_write(request, view, None)
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return self._can_read(request, obj)
        return self._can_write(request, view, obj)


class CookbookViewSetMixin:
    """Wire `CookbookAccessPermission` into a viewset.

    Sets `permission_classes` and filters the queryset through
    `filter_visible` so list endpoints respect the same visibility rules
    as object-level reads.
    """

    permission_classes = [CookbookAccessPermission]

    def get_queryset(self):
        return CookbookAccessPermission.filter_visible(
            self.request, super().get_queryset()
        )
