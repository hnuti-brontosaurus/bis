from concurrent.futures import ThreadPoolExecutor

from django.core.management import call_command
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


@api_view(["post"])
@permission_classes([IsSuperuser])
def manage(request, command):
    ThreadPoolExecutor().submit(call_command, command)
    return Response()
