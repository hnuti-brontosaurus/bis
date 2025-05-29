from bis.admin_permissions import PermissionMixin
from django.contrib.messages import ERROR, INFO
from django.http import HttpResponseRedirect
from django.urls import reverse
from event.models import *
from nested_admin.nested import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline,
)
from other.models import (
    DashboardItem,
    DonationPoints,
    DonationPointsColumn,
    DonationPointsSection,
    DuplicateUser,
)


@admin.register(DuplicateUser)
class DuplicateUserAdmin(PermissionMixin, NestedModelAdmin):
    change_form_template = "bis/duplicate_user_change_form.html"

    list_display = "user", "other", "get_user_info", "get_other_info"
    raw_id_fields = "user", "other"

    list_select_related = "user__address", "other__address"

    search_fields = User.get_search_fields("user__") + User.get_search_fields("other__")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("user__all_emails", "other__all_emails")
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return "get_user_info", "get_other_info"
        return ()

    def get_info(self, user):
        emails = ", ".join(str(email) for email in user.all_emails.all())
        return mark_safe(
            f"{user}<br>Nar: {user.birthday}<br>Adr: {getattr(user, 'address', '')}<br>E-maily: {emails}<br>Tel: {user.phone}"
        )

    @admin.display(description="Primární uživatel")
    def get_user_info(self, obj):
        return self.get_info(obj.user)

    @admin.display(description="Duplicitní uživatel")
    def get_other_info(self, obj):
        return self.get_info(obj.other)

    def response_change(self, request, obj):
        if "_merge_users" in request.POST or "_merge_users_rev" in request.POST:
            if "_merge_users" in request.POST:
                obj.user.merge_with(obj.other)
            else:
                obj.other.merge_with(obj.user)
            return HttpResponseRedirect(reverse("admin:other_duplicateuser_changelist"))

        return super().response_change(request, obj)

    def render_change_form(self, request, context, obj=None, *args, **kwargs):
        if obj:
            context["merge_disabled"] = not obj.can_be_merged_by(request.user)
        return super().render_change_form(request, context, obj, *args, **kwargs)


@admin.action(description="Označit za zpracovné")
def mark_as_resolved(model_admin, request, queryset):
    if not all([obj.has_edit_permission(request.user) for obj in queryset]):
        return model_admin.message_user(
            request, "Nemáš právo editovat vybrané objekty", ERROR
        )
    queryset.update(is_resolved=True)


@admin.register(DashboardItem)
class DashboardItemAdmin(PermissionMixin, NestedModelAdmin):
    list_display = (
        "name",
        "visible_date",
        "date",
        "repeats_every_year",
        "description",
        "get_roles",
    )

    save_as = True

    @admin.display(description="Pro role")
    def get_roles(self, obj):
        return mark_safe("<br>".join(str(role) for role in obj.for_roles.all()))

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("for_roles")


class DonationPointsColumnAdmin(PermissionMixin, NestedTabularInline):
    model = DonationPointsColumn
    extra = 4


class DonationPointsSectionAdmin(PermissionMixin, NestedStackedInline):
    model = DonationPointsSection
    inlines = (DonationPointsColumnAdmin,)
    extra = 2


@admin.register(DonationPoints)
class DonationPointsAdmin(PermissionMixin, NestedModelAdmin):
    inlines = (DonationPointsSectionAdmin,)
    readonly_fields = ("file",)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()
