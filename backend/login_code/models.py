from datetime import timedelta
from random import randint

from bis.models import User
from django.db import models
from django.utils.timezone import now
from rest_framework.exceptions import AuthenticationFailed, Throttled


def get_code():
    return "".join([str(randint(0, 9)) for i in range(4)])


def one_hour_later():
    return now() + timedelta(hours=1)


class ThrottleLog(models.Model):
    key = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def check_throttled(cls, prefix, key, max_count, timedelta_hours):
        if (
            cls.objects.filter(
                key=f"{prefix}_{key}",
                created__gte=now() - timedelta(hours=timedelta_hours),
            ).count()
            > max_count
        ):
            raise Throttled(timedelta_hours * 3600)

    @classmethod
    def add(cls, prefix, key):
        cls.objects.create(key=f"{prefix}_{key}")


class LoginCode(models.Model):
    code = models.CharField(max_length=4, default=get_code)
    valid_till = models.DateTimeField(default=one_hour_later)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_codes")

    @classmethod
    def check_throttled(cls, user):
        ThrottleLog.check_throttled("login_code", user.email, 10, 1)

    @classmethod
    def add_throttled(cls, user):
        ThrottleLog.add("login_code", user.email)

    @classmethod
    def make(cls, user):
        cls.check_throttled(user)
        cls.add_throttled(user)
        return cls.objects.create(user=user)

    @classmethod
    def is_valid(cls, user, code):
        cls.check_throttled(user)

        code = str(code)
        while len(code) < 4:
            code = "0" + code

        login_code = cls.objects.filter(
            user=user, code=code, valid_till__gte=now()
        ).first()

        if login_code is None:
            cls.add_throttled(user)
            raise AuthenticationFailed()
