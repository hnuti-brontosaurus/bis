from os.path import join

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand

from regions.models import Region


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = join(settings.BASE_DIR, "regions", "region_borders", "SPH_KRAJ.shp")
        data = DataSource(path)

        for item in data[0]:
            Region.objects.update_or_create(
                name=item.get("NAZEV_NUTS"), defaults=dict(area=item.geom.wkt)
            )
