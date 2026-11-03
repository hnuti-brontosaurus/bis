from django.core.management.base import BaseCommand
from nest_boxes.models import Area, NestBox


class Command(BaseCommand):
    help = "Recomputes the stored distances to the closest boxes in every area"

    def handle(self, *args, **options):
        for area_id in Area.objects.values_list("id", flat=True):
            NestBox.recompute_distances(area_id)
