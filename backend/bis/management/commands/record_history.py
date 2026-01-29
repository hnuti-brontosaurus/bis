from dateutil.utils import today
from django.core.management.base import BaseCommand

from administration_units.models import AdministrationUnit, BrontosaurusMovement


class Command(BaseCommand):
    def handle(self, *args, **options):
        date = today().date()
        BrontosaurusMovement.get().record_history(date)

        for administration_unit in AdministrationUnit.objects.all():
            if administration_unit.is_active():
                administration_unit.record_history(date)
