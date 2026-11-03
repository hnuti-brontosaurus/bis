from django.conf import settings
from django.db import transaction
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from nest_boxes import e2e_seed


@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def seed(request):
    """Resets the nest box e2e fixture set and returns its ids. TESTING-only."""
    if not settings.TESTING:
        raise Http404
    return Response(e2e_seed.seed())
