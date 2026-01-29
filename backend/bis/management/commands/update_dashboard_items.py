from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.core.management.base import BaseCommand

from other.models import DashboardItem


class Command(BaseCommand):
    def handle(self, *args, **options):
        dashboard_items = DashboardItem.objects.filter(repeats_every_year=True)

        for item in dashboard_items:
            while today().date() > item.date:
                item.date += relativedelta(years=1)
                item.save()
