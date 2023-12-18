from rest_framework.fields import CharField, EmailField
from rest_framework.serializers import Serializer


class LoginCodeSerializer(Serializer):
    email = EmailField()
    code = CharField(max_length=4)
