from django.core.management.base import BaseCommand

from bis.helpers import get_locked_year, with_paused_validation
from event.models import Event


class Command(BaseCommand):
    @with_paused_validation
    def handle(self, *args, **options):
        Event.objects.filter(
            end__year__lte=get_locked_year(), is_archived=False
        ).update(is_archived=True)
