from concurrent.futures import ThreadPoolExecutor

from django.core.management import call_command
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from event.models import Event, EventPhoto, EventPropagationImage


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


@api_view(["post"])
@permission_classes([IsSuperuser])
def manage(request, command):
    ThreadPoolExecutor().submit(call_command, command)
    return Response()


@api_view(["post"])
@permission_classes([IsSuperuser])
def resize_event_photos(request, event_id, size):
    event = get_object_or_404(Event, id=event_id)

    for image in EventPropagationImage.objects.filter(propagation__event=event):
        image.image.resize_original_image(size)

    for photo in EventPhoto.objects.filter(record__event=event):
        photo.photo.resize_original_image(size)

    return Response()
