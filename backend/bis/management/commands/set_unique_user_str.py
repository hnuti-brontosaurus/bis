from collections import defaultdict

from bis.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        to_update = []
        data = defaultdict(list)

        for user in User.objects.all().select_related("address"):
            data[user.get_name(show_nickname=False)].append(user)

        for users in data.values():
            if len(users) == 1:
                fn = lambda _: _.get_name()
            else:
                fn = lambda _: _.get_extended_name()

            for user in users:
                _str = fn(user)
                if user._str != _str:
                    user._str = _str
                    to_update.append(user)

        if to_update:
            User.objects.bulk_update(to_update, ["_str"], batch_size=100)
