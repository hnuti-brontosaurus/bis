import csv
from io import StringIO
from os.path import join

from django.conf import settings
from django.core.management.base import BaseCommand

from bis.models import UserAddress
from regions.models import Region, ZipCode


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = join(settings.BASE_DIR, "regions", "zip_codes", "zv_cobce_psc.csv")
        with open(path, "r", encoding="windows-1250") as file:
            data = StringIO(file.read().strip())

        data = list(csv.reader(data, delimiter=";"))
        header, data = data[0], data[1:]
        region_to_zip_codes = {}
        for line in data:
            region_to_zip_codes.setdefault(line[8], []).append(line[2])

        for region, zip_codes in region_to_zip_codes.items():
            region = Region.objects.get(name__contains=region)
            zip_codes = set(zip_codes)
            for zip_code in zip_codes:
                ZipCode.objects.get_or_create(
                    zip_code=zip_code, defaults=dict(region=region)
                )
