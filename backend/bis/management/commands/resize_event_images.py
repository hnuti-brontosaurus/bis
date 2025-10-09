import os
import re
from os import walk
from pathlib import Path
from shutil import rmtree

import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Downloads all event image-like objects from the production server."

    def add_arguments(self, parser):
        parser.add_argument(
            "--till", type=int, help="Year including till download images."
        )
        parser.add_argument("--size", type=str, help="Size to resize to.")

    def handle(self, *args, **options):
        token = os.environ.get("PROD_API_TOKEN")
        if not token:
            self.stdout.write(
                self.style.ERROR("PROD_API_TOKEN environment variable not set.")
            )
            return

        headers = {"Authorization": f"Token {token}"}
        base_url = "https://bis.brontosaurus.cz/api/"
        session = requests.Session()
        session.headers.update(headers)

        events_url = f"{base_url}frontend/events/"

        page = 1
        while events_url:
            self.stdout.write(f"Fetching events page {page}...")
            response = session.get(events_url)
            response.raise_for_status()
            data = response.json()

            for event in data["results"]:
                self.process_event(event, session, base_url, options)

            events_url = data.get("next")
            page += 1

    def process_event(self, event, session, base_url, options):
        if not event.get("start"):
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping event with no start date: {event['name']}"
                )
            )
            return

        year = event["start"][:4]

        if int(year) >= options["till"]:
            self.stdout.write(self.style.WARNING(f"Skipping event with year: {year}"))
            return

        self.stdout.write(f"Processing event {event['name']}...")
        response = session.post(
            f"{base_url}manage/resize_event_photos/{event['id']}/{options['size']}/"
        )
        response.raise_for_status()
