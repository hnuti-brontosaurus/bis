from bis.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = {"": list(User.objects.all().select_related("address"))}
        new_data = {}

        f1 = lambda user: user.get_name()

        def f2(user):
            _str = [user.get_name()]
            if hasattr(user, "address") and user.address.city:
                _str.append(user.address.city)
            if user.age is not None:
                _str.append(f"{user.age} let")
            return ", ".join(_str)

        for f in [f1, f2]:
            for key, value in data.items():
                if len(value) > 1:
                    for user in value:
                        new_data.setdefault(f(user), []).append(user)

                else:
                    new_data[key] = value

            new_data, data = data, new_data
            new_data.clear()

        to_update = []
        for key, value in data.items():
            for user in value:
                if user._str != key:
                    user._str = key
                    to_update.append(user)

        if to_update:
            User.objects.bulk_update(to_update, ["_str"], batch_size=100)
