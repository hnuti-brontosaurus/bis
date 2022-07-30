from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand

from bis.helpers import print_progress
from bis.models import User
from other.models import DuplicateUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        c = 0
        settings.SKIP_VALIDATION = True
        users = User.objects.all()
        for i, user in enumerate(users):
            print_progress('merging users', i, len(users))
            for other in User.objects.filter(id__gt=user.id, first_name=user.first_name, last_name=user.last_name):
                if user.birthday and other.birthday and user.birthday != other.birthday:
                    DuplicateUser.objects.get_or_create(user=user, other=other)
                    continue

                print('merging ', user, ' with ', other)
                try:
                    user.merge_with(other)
                except ValidationError:
                    pass

        print('same name, different birthday', c)
