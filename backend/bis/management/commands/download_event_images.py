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

    def handle(self, *args, **options):
        output_dir = Path("/event_images")
        output_dir.mkdir(parents=True, exist_ok=True)

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

        downloaded_count = 0
        skipped_count = 0
        page = 1
        while events_url:
            self.stdout.write(f"Fetching events page {page}...")
            response = session.get(events_url)
            response.raise_for_status()
            data = response.json()

            for event in data["results"]:
                downloaded, skipped = self.process_event(
                    event, output_dir, session, base_url, options["till"]
                )
                downloaded_count += downloaded
                skipped_count += skipped

            events_url = data.get("next")
            page += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished downloading event images. Downloaded: {downloaded_count}, Skipped: {skipped_count}"
            )
        )

        for folder, _, _ in reversed(list(walk(output_dir))):
            if not os.listdir(folder):
                rmtree(folder)

    def process_event(self, event, output_dir, session, base_url, till):
        if not event.get("start"):
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping event with no start date: {event['name']}"
                )
            )
            return 0, 0

        year = event["start"][:4]

        if int(year) >= till:
            self.stdout.write(self.style.WARNING(f"Skipping event with year: {year}"))
            return 0, 0

        if not event.get("group") or not event.get("group").get("name"):
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping event with no group name: {event['name']}"
                )
            )
            return 0, 0

        group_name = self.sanitize_filename(event["group"]["name"])
        event_name = self.sanitize_filename(event["name"])

        event_dir = output_dir / year / group_name / event_name
        event_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write(f"Processing event: {event['name']}")

        event_id = event["id"]

        image_types = {
            "propagation/images": "image",
            "record/photos": "photo",
            "record/attendance_list_pages": "page",
            "finance/receipts": "receipt",
        }

        downloaded_count = 0
        skipped_count = 0
        for image_type, field_name in image_types.items():
            downloaded, skipped = self.download_files_for_type(
                event_id, event_dir, session, base_url, image_type, field_name
            )
            downloaded_count += downloaded
            skipped_count += skipped

        return downloaded_count, skipped_count

    def download_files_for_type(
        self, event_id, event_dir, session, base_url, image_type, field_name
    ):
        image_type_slug = self.sanitize_filename(image_type)
        image_type_dir = event_dir / image_type_slug
        image_type_dir.mkdir(parents=True, exist_ok=True)

        downloaded_count = 0
        skipped_count = 0

        url = f"{base_url}frontend/events/{event_id}/{image_type}/"
        while url:
            try:
                response = session.get(url)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"  Error fetching {url}: {e}"))
                return 0, 0

            for item in data["results"]:
                image_url = item.get(field_name)
                if not image_url:
                    continue

                if isinstance(image_url, dict):
                    image_url = image_url["original"]

                filename = self.sanitize_filename(
                    image_url.split("/")[-1].split("?")[0]
                )
                filepath = image_type_dir / filename

                if filepath.exists():
                    self.stdout.write(f"  Skipping existing file: {filepath}")
                    skipped_count += 1
                    continue

                self.stdout.write(f"  Downloading {image_url} to {filepath}")
                try:
                    image_response = session.get(image_url, stream=True)
                    image_response.raise_for_status()
                    with open(filepath, "wb") as f:
                        for chunk in image_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded_count += 1
                except requests.exceptions.RequestException as e:
                    self.stdout.write(
                        self.style.ERROR(f"  Error downloading {image_url}: {e}")
                    )

            url = data.get("next")

        return downloaded_count, skipped_count

    def sanitize_filename(self, filename):
        return re.sub(r'[<>:"/\\|?*]', "_", filename)
