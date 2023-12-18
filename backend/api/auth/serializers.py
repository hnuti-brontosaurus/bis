from rest_framework.fields import CharField, EmailField, IntegerField
from rest_framework.serializers import Serializer


class LoginRequestSerializer(Serializer):
    email = EmailField()
    password = CharField()


class SendVerificationLinkRequestSerializer(Serializer):
    email = EmailField()


class ResetPasswordRequestSerializer(Serializer):
    email = EmailField()
    code = CharField()
    password = CharField()


class TokenResponse(Serializer):
    token = CharField()


class UserIdResponse(Serializer):
    id = IntegerField()
