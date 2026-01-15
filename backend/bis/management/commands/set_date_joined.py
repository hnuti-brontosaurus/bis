from django.core.management.base import BaseCommand
from django.utils.datetime_safe import date

from bis.helpers import print_progress
from bis.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all().prefetch_related(
            "memberships",
            "qualifications",
            "events_where_was_organizer",
            "participated_in_events__event",
        )
        to_update = []
        for i, user in enumerate(users):
            print_progress("setting date joined", i, len(users))
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

        User.objects.bulk_update(users, ["date_joined"], batch_size=100)
