from collections import defaultdict

from django.core.management.base import BaseCommand

from bis.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        to_update = []
        data = defaultdict(list)

        for user in User.objects.all().select_related("address"):
            data[user.get_name(show_nickname=False)].append(user)

        for users in data.values():
            extended = len(users) > 1

            for user in users:
                _str = user.get_extended_name() if extended else user.get_name()
                if user._str != _str:
                    user._str = _str
                    to_update.append(user)

        if to_update:
            User.objects.bulk_update(to_update, ["_str"], batch_size=100)
