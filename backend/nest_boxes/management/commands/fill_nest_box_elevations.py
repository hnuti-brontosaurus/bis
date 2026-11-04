from itertools import batched
from time import sleep

import requests
from django.core.management.base import BaseCommand
from django.utils.timezone import localdate
from nest_boxes.boxes import update_box
from nest_boxes.models import NestBox

DATASET = "eudem25m"
URL = f"https://api.opentopodata.org/v1/{DATASET}"
# The public API's limits
POINTS_PER_REQUEST = 100
SECONDS_BETWEEN_REQUESTS = 1


class Command(BaseCommand):
    help = "Fills in the elevation of boxes without one, from OpenTopoData"

    def handle(self, *args, **options):
        boxes = NestBox.objects.filter(elevation=None)
        today = localdate()
        for number, chunk in enumerate(batched(boxes, POINTS_PER_REQUEST)):
            if number:
                sleep(SECONDS_BETWEEN_REQUESTS)
            locations = "|".join(f"{box.location.y},{box.location.x}" for box in chunk)
            response = requests.post(URL, json={"locations": locations}, timeout=30)
            response.raise_for_status()
            for box, result in zip(chunk, response.json()["results"], strict=True):
                # Outside the dataset's coverage, eudem25m answers null
                if result["elevation"] is not None:
                    update_box(
                        box, {"elevation": round(result["elevation"])}, None, today
                    )
