from dataclasses import dataclass
from datetime import timedelta
from random import randint

from bis.models import User
from django.core.cache import cache
from django.db import models
from django.utils.timezone import now
from rest_framework.exceptions import AuthenticationFailed, Throttled


def get_code():
    return "".join([str(randint(0, 9)) for i in range(4)])


def one_hour_later():
    return now() + timedelta(hours=1)


@dataclass(frozen=True)
class Throttle:
    prefix: str
    max_count: int
    window_hours: int

    def _key(self, key):
        return f"throttle:{self.prefix}:{key}"

    def check(self, key):
        if (cache.get(self._key(key)) or 0) > self.max_count:
            raise Throttled(self.window_hours * 3600)

    def add(self, key):
        cache_key = self._key(key)
        try:
            cache.incr(cache_key)
        except ValueError:
            cache.set(cache_key, 1, timeout=self.window_hours * 3600)


login_code_throttle = Throttle("login_code", max_count=10, window_hours=1)
cookbook_login_throttle = Throttle("cookbook_login", max_count=10, window_hours=1)
get_unknown_user_throttle = Throttle("get_unknown_user", max_count=5, window_hours=24)
guess_birthday_throttle = Throttle("guess_birthday", max_count=5, window_hours=24)


class LoginCode(models.Model):
    code = models.CharField(max_length=4, default=get_code)
    valid_till = models.DateTimeField(default=one_hour_later)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_codes")

    def __str__(self):
        return f"login_code.{self.id}"

    @classmethod
    def check_throttled(cls, user):
        login_code_throttle.check(user.email)

    @classmethod
    def add_throttled(cls, user):
        login_code_throttle.add(user.email)

    @classmethod
    def make(cls, user):
        cls.check_throttled(user)
        cls.add_throttled(user)
        return cls.objects.create(user=user)

    @classmethod
    def remove_expired(cls):
        cls.objects.filter(valid_till__lt=now()).delete()

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
