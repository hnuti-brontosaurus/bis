from bis.models import User
from django.conf import settings
from django.core.management import call_command
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([AllowAny])
def seed(request):
    """Idempotent cookbook seed for the e2e global setup. TESTING-only."""
    if not settings.TESTING:
        raise Http404
    call_command("testing_db", "cookbook")
    return Response({"ok": True})


@api_view(["POST"])
@permission_classes([AllowAny])
def auth_token(request):
    """Return the auth token for a seeded user, so the e2e runner needs no
    shell access to this container. TESTING-only."""
    if not settings.TESTING:
        raise Http404
    email = request.data.get("email")
    user = User.objects.get(email=email)
    return Response({"token": user.auth_token.key})
