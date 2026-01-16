from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.utils.datetime_safe import date

from bis.helpers import print_progress
from bis.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        total_users = User.objects.count()
        users = User.objects.all().prefetch_related(
            "memberships",
            "qualifications",
            "events_where_was_organizer",
            "participated_in_events__event",
        )
        paginator = Paginator(users, 500)

        processed = 0
        for page_num in paginator.page_range:
            to_update = []
            for user in paginator.page(page_num):
                print_progress("setting date joined", processed, total_users)
                processed += 1

                dates = [user.date_joined]

                for membership in user.memberships.all():
                    dates.append(date(membership.year, 1, 1))

                for qualification in user.qualifications.all():
                    dates.append(qualification.valid_since)

                for event in user.events_where_was_organizer.all():
                    dates.append(event.start)

                for event in user.participated_in_events.all():
                    dates.append(event.event.start)

                if user.date_joined != min(dates):
                    user.date_joined = min(dates)
                    to_update.append(user)

            if to_update:
                User.objects.bulk_update(to_update, ["date_joined"], batch_size=100)
