from rest_framework.permissions import BasePermission

from bis.permissions import Permissions


class BISPermissions(BasePermission):
    def has_permission(self, request, view):
        return self.has_object_permission(request, view, None)

    def has_object_permission(self, request, view, obj):
        perms = Permissions(request.user, view.serializer_class.Meta.model, "frontend")

        if view.action in ["retrieve", "list"]:
            return perms.has_view_permission(obj)

        if view.action in ["create"]:
            return perms.has_add_permission(obj)

        if view.action in ["update", "partial_update"]:
            return perms.has_change_permission(obj)

        if view.action in ["destroy"]:
            return perms.has_delete_permission(obj)

        assert False
