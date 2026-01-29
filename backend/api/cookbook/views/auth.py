from time import sleep

import requests
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError
from rest_framework.fields import CharField, EmailField, IntegerField
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api.cookbook.serializers import ChefSerializer
from api.helpers import parse_request_data
from bis.models import User
from login_code.models import ThrottleLog


def get_user_data(user):
    data = {
        "is_authenticated": user.is_authenticated,
        "is_chef": user.is_authenticated and user.is_chef,
        "is_editor": user.is_authenticated and user.is_editor,
        "user": {},
        "chef": {},
    }
    if data["is_authenticated"]:
        data["user"] = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "token": user.auth_token.key,
        }
        data["chef"] = {"user_id": user.id}

    if data["is_chef"]:
        data["chef"] = ChefSerializer(user.chef).data

    return Response(data)


@api_view(["get"])
def whoami(request):
    return get_user_data(request.user)


class CheckEmailSerializer(Serializer):
    email = EmailField()


@extend_schema(request=CheckEmailSerializer)
@api_view(["post"])
@parse_request_data(CheckEmailSerializer)
def check_email(request, data):
    return Response(User.objects.filter(all_emails__email=data["email"]).exists())


class ValidatePasswordSerializer(Serializer):
    password = CharField()


@extend_schema(request=ValidatePasswordSerializer)
@api_view(["post"])
@parse_request_data(ValidatePasswordSerializer)
def check_password(request, data):
    try:
        validate_password(data["password"])
    except DjangoValidationError as e:
        raise ValidationError(e.messages)
    return Response([])


class RegisterSerializer(Serializer):
    email = EmailField()
    first_name = CharField()
    last_name = CharField()
    password = CharField()
    response = CharField()


@extend_schema(request=RegisterSerializer)
@api_view(["post"])
@parse_request_data(RegisterSerializer)
def register(request, data):
    response = requests.post(
        "https://hcaptcha.com/siteverify",
        {"response": data["response"], "secret": settings.HCAPTCHA_SECRET},
    )
    assert response.json()["success"]

    try:
        validate_password(data["password"])
    except DjangoValidationError as e:
        raise ValidationError(e.messages)

    user = User.objects.create(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
    )
    user.set_password(data["password"])
    user.save()
    return get_user_data(user)


class LoginSerializer(Serializer):
    email = EmailField()
    password = CharField()


@extend_schema(request=LoginSerializer)
@api_view(["post"])
@parse_request_data(LoginSerializer)
def login(request, data):
    user = User.objects.filter(all_emails__email=data["email"].lower()).first()
    if not user:
        raise AuthenticationFailed()

    # ThrottleLog.check_throttled("cookbook_login", user.email, 10, 1)

    if not user.check_password(data["password"]):
        if data["password"] != f"Token {user.auth_token.key}":
            ThrottleLog.add("cookbook_login", user.email)
            raise AuthenticationFailed()

    return get_user_data(user)
