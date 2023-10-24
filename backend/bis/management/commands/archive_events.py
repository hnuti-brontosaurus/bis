from datetime import date

from django.core.management.base import BaseCommand

from bis.helpers import with_paused_validation
from event.models import Event


class Command(BaseCommand):
    @with_paused_validation
    def handle(self, *args, **options):
        today = date.today()
        year_to_archive = today.year - 1
        if today.month < 3:
            year_to_archive -= 1

        Event.objects.filter(
            end__lte=date(year_to_archive, 12, 31), is_archived=False
        ).update(is_archived=True)
