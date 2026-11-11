from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Max, ProtectedError, Q
from nest_boxes.checks import BatchClosed
from nest_boxes.models import HelpArticle, NestBox
from nest_boxes.permissions import can_manage, is_manager, manages_all
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.serializers import as_serializer_error


class Gone(APIException):
    status_code = 410
    default_detail = "Obchůzka je uzavřená a nic dalšího nepřijímá."
    default_code = "batch_closed"


class NestBoxAPIMixin:
    """The SPA is signed in by the session the BIS login starts, see CLAUDE.md."""

    authentication_classes = [SessionAuthentication]

    def handle_exception(self, exc):
        if isinstance(exc, DjangoValidationError):
            exc = ValidationError(as_serializer_error(exc))
        elif isinstance(exc, BatchClosed):
            exc = Gone()
        elif isinstance(exc, ProtectedError):
            exc = ValidationError("Nejde smazat, dosud se to používá.")
        return super().handle_exception(exc)


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return is_manager(request.user)


class IsBudkarOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or manages_all(request.user)


def require_manage(user, area):
    if not can_manage(user, area):
        raise PermissionDenied


def box_queryset():
    return (
        NestBox.objects.with_season_state()
        .annotate(
            last_checked_on=Max("checks__date", filter=Q(checks__is_confirmed=True))
        )
        .select_related("created_by")
    )


def help_articles():
    """Every article, created on first lookup so they survive `testing_db dev`'s flush."""
    existing = set(HelpArticle.objects.values_list("slug", flat=True))
    HelpArticle.objects.bulk_create(
        HelpArticle(slug=slug)
        for slug in HelpArticle.Slug.values
        if slug not in existing
    )
    return HelpArticle.objects.all()
