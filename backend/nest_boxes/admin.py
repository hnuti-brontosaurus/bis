from bis.admin_permissions import PermissionMixin
from django import forms
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.urls import path
from nest_boxes.models import (
    Area,
    Check,
    CheckPhoto,
    HelpArticle,
    HelpImage,
    NestBox,
    NestBoxHistory,
)
from nest_boxes.old_import.run import import_dump


class BoxInline(PermissionMixin, admin.TabularInline):
    model = NestBox
    fields = ("name", "status", "type")
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


class OldDumpForm(forms.Form):
    dump = forms.FileField(label="SQL dump z Admineru")


@admin.register(NestBox)
class NestBoxAdmin(PermissionMixin, GISModelAdmin):
    list_display = (
        "name",
        "area",
        "status",
        "type",
        "is_verified",
        "closest_distance",
        "closest_same_type_distance",
    )
    list_filter = ("status", "type")
    search_fields = ("name", "previous_names", "area__name")
    autocomplete_fields = ("area", "created_by")
    readonly_fields = (
        "region",
        "closest_distance",
        "closest_same_type_distance",
        "created_at",
    )
    inlines = (HistoryInline,)
    change_list_template = "nest_boxes/nest_box_change_list.html"

    def get_queryset(self, request):
        return super().get_queryset(request).with_is_verified()

    def get_urls(self):
        return [
            path(
                "import/",
                self.admin_site.admin_view(self.import_view),
                name="nest_boxes_nestbox_import",
            ),
            *super().get_urls(),
        ]

    def import_view(self, request):
        """The import command for those who can't reach the server's shell."""
        if not request.user.is_superuser:
            raise PermissionDenied
        form = OldDumpForm(request.POST or None, request.FILES or None)
        report = None
        if form.is_valid():
            report = import_dump(form.cleaned_data["dump"].read().decode("utf-8"))
        return TemplateResponse(
            request,
            "nest_boxes/import_old_nest_boxes.html",
            {
                **self.admin_site.each_context(request),
                "opts": self.model._meta,
                "title": "Import ze starých budek",
                "form": form,
                "report": "\n".join(report) if report else None,
            },
        )

    @admin.display(boolean=True, description="Ověřena?", ordering="is_verified")
    def is_verified(self, box):
        return box.is_verified


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
        "entered_by",
        "confirmed_by",
        "cleaned_by",
    )
    readonly_fields = ("season", "batch")
    inlines = (CheckPhotoInline,)


class HelpImageInline(PermissionMixin, admin.TabularInline):
    model = HelpImage
    extra = 0


@admin.register(HelpArticle)
class HelpArticleAdmin(PermissionMixin, admin.ModelAdmin):
    list_display = ("slug", "title")
    inlines = (HelpImageInline,)
