import logging

from bis.drive import (
    build_drive_service,
    get_existing_names,
    get_or_create_folder,
    upload_file,
)
from django.conf import settings
from django.core.management.base import BaseCommand
from event.models import Event


class Command(BaseCommand):
    help = (
        "Uploads all event files for 'Modrý Kámen' administration unit to Google Drive."
    )

    def handle(self, *args, **options):
        service = build_drive_service()
        folder_id = get_or_create_folder(
            service,
            "Modrý kámen export",
            parent_id=settings.GOOGLE_SHARED_DRIVE_ID,
        )
        logging.info(f"Using Drive folder id: {folder_id}")

        events = Event.objects.filter(
            administration_units__abbreviation="Modrý Kámen"
        ).distinct()
        logging.info(f"Found {events.count()} events")

        uploaded = 0
        for event in events:
            date_str = event.start.strftime("%Y-%m-%d") if event.start else "0000-00-00"
            files = [
                (f"{date_str} - {event.name} - {file_path.name}", file_path.path)
                for file_path in self._collect_files(event)
            ]
            if not files:
                continue
            existing = get_existing_names(
                service, folder_id, [name for name, _ in files]
            )
            for drive_name, path in files:
                if drive_name in existing:
                    logging.info(f"  Skipping (already exists): {drive_name}")
                    continue
                logging.info(f"  Uploading: {drive_name}")
                upload_file(service, folder_id, drive_name, path)
                uploaded += 1

        logging.info(f"Done. Uploaded: {uploaded}")

    def _collect_files(self, event):
        if hasattr(event, "finance"):
            if event.finance.budget:
                yield event.finance.budget
            for receipt in event.finance.receipts.all():
                if receipt.receipt:
                    yield receipt.receipt
        if hasattr(event, "propagation"):
            for image in event.propagation.images.all():
                if image.image:
                    yield image.image
        if hasattr(event, "record"):
            for page in event.record.attendance_list_pages.all():
                if page.page:
                    yield page.page
            for photo in event.record.photos.all():
                if photo.photo:
                    yield photo.photo
