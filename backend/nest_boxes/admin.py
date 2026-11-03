from bis.admin_permissions import PermissionMixin
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from nest_boxes.models import (
    Area,
    Batch,
    Check,
    CheckPhoto,
    HelpArticle,
    HelpImage,
    NestBox,
    NestBoxHistory,
)


class BoxInline(PermissionMixin, admin.TabularInline):
    model = NestBox
    fields = ("name", "status", "condition", "type", "is_verified", "is_confirmed")
    show_change_link = True
    extra = 0


@admin.register(Area)
class AreaAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = ("name", "administration_unit")
    search_fields = ("name",)
    autocomplete_fields = ("administration_unit",)
    inlines = (BoxInline,)


class HistoryInline(PermissionMixin, admin.TabularInline):
    model = NestBoxHistory
    fields = ("date", "user", "box_check", "changes")
    readonly_fields = fields
    extra = 0


@admin.register(NestBox)
class NestBoxAdmin(PermissionMixin, GISModelAdmin):
    list_display = (
        "name",
        "area",
        "status",
        "condition",
        "type",
        "is_verified",
        "is_confirmed",
        "closest_distance",
        "closest_same_type_distance",
    )
    list_filter = ("status", "condition", "type", "is_verified", "is_confirmed")
    search_fields = ("name", "previous_names", "area__name")
    autocomplete_fields = ("area", "created_by", "batch")
    readonly_fields = (
        "region",
        "closest_distance",
        "closest_same_type_distance",
        "created_at",
    )
    inlines = (HistoryInline,)


class CheckPhotoInline(PermissionMixin, admin.TabularInline):
    model = CheckPhoto
    extra = 0


@admin.register(Check)
class CheckAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = ("box", "date", "season", "found", "cleaning", "is_confirmed")
    list_filter = ("season", "is_confirmed", "found", "cleaning", "is_historical")
    search_fields = ("box__name", "box__area__name")
    autocomplete_fields = (
        "box",
        "batch",
        "entered_by",
        "confirmed_by",
        "cleaned_by",
    )
    readonly_fields = ("season",)
    inlines = (CheckPhotoInline,)


@admin.register(Batch)
class BatchAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = ("name", "area", "created_at", "closed_at", "confirmed_at")
    search_fields = ("name", "area__name")
    autocomplete_fields = ("area", "boxes", "cleaned_by", "created_by", "confirmed_by")
    readonly_fields = ("token", "created_at")


class HelpImageInline(PermissionMixin, admin.TabularInline):
    model = HelpImage
    extra = 0


@admin.register(HelpArticle)
class HelpArticleAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = ("slug", "title")
    inlines = (HelpImageInline,)
