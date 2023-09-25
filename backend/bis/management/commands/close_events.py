from datetime import date

from django.core.management.base import BaseCommand

from bis.helpers import with_paused_validation
from event.models import Event


class Command(BaseCommand):
    @with_paused_validation
    def handle(self, *args, **options):
        today = date.today()
        year_to_close = today.year - 1
        if today.month < 3:
            year_to_close -= 1

        Event.objects.filter(
            end__lte=date(year_to_close, 12, 31), is_closed=False
        ).update(is_closed=True)
