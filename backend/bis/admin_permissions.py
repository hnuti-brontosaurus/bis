from bis.permissions import Permissions
from django.contrib.admin.options import InlineModelAdmin


class PermissionMixin:
    def get_queryset(self, request):
        self.request = request
        queryset = super().get_queryset(request)

        if isinstance(self, InlineModelAdmin):
            return queryset

        queryset = Permissions(request.user, self.model, "backend").filter_queryset(
            queryset
        )

        if ordering := self.get_ordering(request):
            queryset = queryset.order_by(*ordering)

        return queryset

    def has_view_permission(self, request, obj=None):
        # individual objects are filtered using get_queryset,
        # this is used only for disabling whole admin model
        return Permissions(request.user, self.model, "backend").has_view_permission(obj)

    def has_add_permission(self, request, obj=None):
        return Permissions(request.user, self.model, "backend").has_add_permission(obj)

    def has_change_permission(self, request, obj=None):
        return Permissions(request.user, self.model, "backend").has_change_permission(
            obj
        )

    def has_delete_permission(self, request, obj=None):
        return Permissions(request.user, self.model, "backend").has_delete_permission(
            obj
        )

    def get_extra(self, request, obj=None, **kwargs):
        if self.has_add_permission(request, obj):
            return super().get_extra(request, obj, **kwargs)

        return 0


class ReadonlyMixin:
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
