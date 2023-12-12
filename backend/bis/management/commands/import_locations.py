import re
from os import makedirs
from os.path import basename, exists, join
from urllib import request
from urllib.request import urlretrieve

import requests
from bis.helpers import print_progress
from bis.models import (
    Location,
    LocationContactPerson,
    LocationPatron,
    LocationPhoto,
    User,
)
from bis.signals import with_paused_user_str_signal
from categories.models import LocationAccessibilityCategory, LocationProgramCategory
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from requests import HTTPError


class Command(BaseCommand):
    base_url = "https://www.mapotic.com/api/v1/maps/739/"

    categories_map = {
        2371: dict(
            program=LocationProgramCategory.objects.get(slug="nature"),
            for_beginners=True,
            is_unexplored=False,
        ),
        2376: dict(
            program=LocationProgramCategory.objects.get(slug="nature"),
            for_beginners=False,
            is_unexplored=False,
        ),
        2377: dict(
            program=LocationProgramCategory.objects.get(slug="nature"),
            for_beginners=False,
            is_unexplored=True,
        ),
        32943: dict(
            program=LocationProgramCategory.objects.get(slug="nature"),
            for_beginners=False,
            is_unexplored=True,
        ),
        2378: dict(
            program=LocationProgramCategory.objects.get(slug="monuments"),
            for_beginners=True,
            is_unexplored=False,
        ),
        2379: dict(
            program=LocationProgramCategory.objects.get(slug="monuments"),
            for_beginners=False,
            is_unexplored=False,
        ),
        2380: dict(
            program=LocationProgramCategory.objects.get(slug="monuments"),
            for_beginners=False,
            is_unexplored=True,
        ),
        32944: dict(
            program=LocationProgramCategory.objects.get(slug="monuments"),
            for_beginners=False,
            is_unexplored=True,
        ),
    }

    location_accessibility_map = {
        "629m": LocationAccessibilityCategory.objects.get(slug="good"),
        "wqrv": LocationAccessibilityCategory.objects.get(slug="good"),
        "x0b3": LocationAccessibilityCategory.objects.get(slug="ok"),
        "i0km": LocationAccessibilityCategory.objects.get(slug="ok"),
        "jckv": LocationAccessibilityCategory.objects.get(slug="bad"),
        "yojk": LocationAccessibilityCategory.objects.get(slug="bad"),
    }

    def get_info(self):
        return requests.get(self.base_url).json()

    def get_locations(self):
        return requests.get(self.base_url + "pois.geojson/").json()

    def get_location_data(self, id):
        return requests.get(self.base_url + f"public-pois/{id}/").json()

    def get_images(self, id):
        return requests.get(self.base_url + f"pois/{id}/images/").json()

    def parse_attribute(self, attr):
        if attr["attribute"]["id"] == 2259:
            return dict(is_full=attr["value"][0] == "nrrx")
        if attr["attribute"]["id"] == 2260:
            return dict(description=attr["value"])
        if attr["attribute"]["id"] == 2261:
            return dict(volunteering_work=attr["value"])
        if attr["attribute"]["id"] == 2276:
            return dict(volunteering_work_done=attr["value"])
        if attr["attribute"]["id"] == 2262:
            return dict(volunteering_work_goals=attr["value"])
        if attr["attribute"]["id"] == 2263:
            return dict(facilities=attr["value"])
        if attr["attribute"]["id"] == 2267:
            return dict(options_around=attr["value"])
        if attr["attribute"]["id"] in [2264, 2265]:
            attr_name = (
                "patron" if attr["attribute"]["id"] == 2264 else "contact_person"
            )
            obj_class = (
                LocationPatron
                if attr["attribute"]["id"] == 2264
                else LocationContactPerson
            )
            match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", attr["value"])
            if not match:
                return {}
            email = match.group(0).lower()

            obj = None
            if email:
                obj = obj_class(
                    first_name=attr["value"][:62],
                    last_name=attr["value"][62:124],
                    email=email,
                )

            return {attr_name: obj}

        if attr["attribute"]["id"] == 2266:
            return dict(web=attr["value"])
        if attr["attribute"]["id"] == 8118:
            return dict(
                accessibility_from_brno=self.location_accessibility_map[
                    attr["value"][0]
                ]
            )
        if attr["attribute"]["id"] == 8119:
            return dict(
                accessibility_from_prague=self.location_accessibility_map[
                    attr["value"][0]
                ]
            )

        raise RuntimeError("unknown attribute")

    def parse_attributes(self, attrs):
        res = {}
        for attr in attrs:
            res.update(self.parse_attribute(attr))

        return res

    @with_paused_user_str_signal
    def handle(self, *args, **options):
        dir_path = join(settings.BASE_DIR, "media", "location_photos")
        makedirs(dir_path, exist_ok=True)

        opener = request.build_opener()
        opener.addheaders = [("User-agent", "Mozilla/5.0")]
        request.install_opener(opener)
        features = self.get_locations()["features"]
        for i, feature in enumerate(features):
            print_progress("importing locations", i, len(features))
            assert feature["type"] == "Feature"
            assert feature["geometry"]["type"] == "Point"
            _import_id = feature["properties"]["id"]
            point = Point(feature["geometry"]["coordinates"], srid=4326)
            data = self.get_location_data(_import_id)

            location = Location.objects.update_or_create(
                _import_id=f"m{_import_id}",
                defaults=dict(
                    name=feature["properties"]["name"],
                    is_traditional=True,
                    **self.categories_map[feature["properties"]["category"]],
                    **self.parse_attributes(data["attributes_values"]),
                    gps_location=point,
                ),
            )[0]

            for image in self.get_images(_import_id):
                path = image["image"]["origin"]["path"]
                file_name = basename(path)

                file_path = join(dir_path, file_name)
                if not exists(file_path):
                    try:
                        urlretrieve(path, file_path)
                    except HTTPError:
                        pass
                if exists(file_path):
                    LocationPhoto.objects.get_or_create(
                        location=location, photo=join("location_photos", file_name)
                    )
