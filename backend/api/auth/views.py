from api.auth.serializers import (
    LoginRequestSerializer,
    ResetPasswordRequestSerializer,
    SendVerificationLinkRequestSerializer,
    TokenResponse,
    UserIdResponse,
)
from api.helpers import parse_request_data
from bis.models import User
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import OpenApiResponse, extend_schema
from login_code.models import LoginCode
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_429_TOO_MANY_REQUESTS,
)

from bis import emails


def login_and_return_token(request, user):
    django_login(request._request, user)
    return Response({"token": user.auth_token.key})


@extend_schema(responses=UserIdResponse())
@api_view()
@permission_classes([IsAuthenticated])
def whoami(request):
    return Response({"id": request.user.id})


@extend_schema(
    request=LoginRequestSerializer,
    responses={
        HTTP_200_OK: TokenResponse,
        HTTP_401_UNAUTHORIZED: OpenApiResponse(
            description="E-mail or password incorrect"
        ),
        HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(description="Too many requests"),
    },
)
@api_view(["post"])
@parse_request_data(LoginRequestSerializer)
def login(request, data):
    user = User.objects.filter(all_emails__email=data["email"].lower()).first()
    if not user:
        raise AuthenticationFailed()

    LoginCode.check_throttled(user)

    if not user.check_password(data["password"]):
        if data["password"] != f"Token {user.auth_token.key}":
            LoginCode.add_throttled(user)
            raise AuthenticationFailed()

    return login_and_return_token(request, user)


@extend_schema(
    request=SendVerificationLinkRequestSerializer,
    responses={
        HTTP_204_NO_CONTENT: None,
        HTTP_404_NOT_FOUND: OpenApiResponse(description="User with email not found"),
        HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(description="Too many requests"),
    },
)
@api_view(["post"])
@parse_request_data(SendVerificationLinkRequestSerializer)
def send_verification_link(request, data):
    email = data["email"].lower()
    user = User.objects.filter(all_emails__email=email).first()
    if not user:
        raise NotFound()
    login_code = LoginCode.make(user)
    emails.password_reset_link(user, email, login_code)

    return Response(status=HTTP_204_NO_CONTENT)


@extend_schema(
    request=ResetPasswordRequestSerializer,
    responses={
        HTTP_200_OK: TokenResponse,
        HTTP_404_NOT_FOUND: OpenApiResponse(description="User with email not found"),
        HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(description="Too many requests"),
    },
)
@api_view(["post"])
@parse_request_data(ResetPasswordRequestSerializer)
def reset_password(request, data):
    user = User.objects.filter(all_emails__email=data["email"].lower()).first()
    if not user:
        raise NotFound()

    try:
        validate_password(data["password"], user)
    except DjangoValidationError as e:
        raise ValidationError(e.messages)

    LoginCode.is_valid(user, data["code"])
    user.set_password(data["password"])
    user.save()

    return login_and_return_token(request, user)


@extend_schema(request=None, responses={HTTP_204_NO_CONTENT: None})
@api_view(["post"])
def logout(request):
    django_logout(request)
    return Response(status=HTTP_204_NO_CONTENT)
