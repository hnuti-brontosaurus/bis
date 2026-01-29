from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from django.contrib.admin import EmptyFieldListFilter
from more_admin_filters import MultiSelectRelatedDropdownFilter
from nested_admin.nested import NestedModelAdmin, NestedTabularInline

from bis.admin_permissions import PermissionMixin
from game_book.models import *


class CommentFileAdmin(PermissionMixin, NestedTabularInline):
    model = CommentFile
    classes = ("collapse",)


class CommentAdmin(PermissionMixin, NestedTabularInline):
    inlines = (CommentFileAdmin,)
    model = Comment
    autocomplete_fields = ("author",)
    classes = ("collapse",)


class PlayedAtFileAdmin(PermissionMixin, NestedTabularInline):
    model = PlayedAtFile
    classes = ("collapse",)


class PlayedAtAdmin(PermissionMixin, NestedTabularInline):
    model = PlayedAt
    inlines = (PlayedAtFileAdmin,)
    autocomplete_fields = ("event",)
    classes = ("collapse",)


class GameFileAdmin(PermissionMixin, NestedTabularInline):
    model = GameFile
    classes = ("collapse",)


@admin.register(Game)
class GameAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "short_description", "contributor"
    search_fields = "name", "short_description"
    list_filter = (
        AutocompleteFilterFactory("Contributor", "contributor"),
        "is_original",
        AutocompleteFilterFactory("Administration unit", "administration_unit"),
        "stars",
        "is_verified",
        ("tags", MultiSelectRelatedDropdownFilter),
        ("physical_category", MultiSelectRelatedDropdownFilter),
        ("mental_category", MultiSelectRelatedDropdownFilter),
        ("location_category", MultiSelectRelatedDropdownFilter),
        ("participant_number_category", MultiSelectRelatedDropdownFilter),
        ("participant_age_category", MultiSelectRelatedDropdownFilter),
        ("game_length_category", MultiSelectRelatedDropdownFilter),
        ("preparation_length_category", MultiSelectRelatedDropdownFilter),
        ("organizers_number_category", MultiSelectRelatedDropdownFilter),
        ("material_requirement_category", MultiSelectRelatedDropdownFilter),
    )

    inlines = GameFileAdmin, CommentAdmin, PlayedAtAdmin
    autocomplete_fields = (
        "contributor",
        "administration_unit",
        "thumbs_up",
        "favourites",
        "watchers",
    )


@admin.register(GameList)
class GameListAdmin(PermissionMixin, NestedModelAdmin):
    list_display = "name", "owner"
    list_filter = (AutocompleteFilterFactory("Owner", "owner"),)
    autocomplete_fields = "owner", "games"
