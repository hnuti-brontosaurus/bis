import logging
import os
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from bis.drive import (
    build_drive_service,
    get_existing_names,
    get_or_create_folder,
    list_subfolders,
    sanitize_name,
    upload_file,
)
from event.models import Event


class Command(BaseCommand):
    help = "Daily incremental export of all event files to Google Drive."

    def add_arguments(self, parser):
        parser.add_argument("--root-folder", default="BIS export")
        parser.add_argument(
            "--all",
            action="store_true",
            help="Ignore mtime filter; consider every file.",
        )
        parser.add_argument(
            "--since-days",
            type=int,
            default=2,
            help="Only consider files with mtime within this many days.",
        )

    def handle(self, *args, **options):
        service = build_drive_service()

        root_id = get_or_create_folder(
            service,
            options["root_folder"],
            parent_id=settings.GOOGLE_SHARED_DRIVE_ID,
        )
        existing_event_folders = list_subfolders(service, root_id)

        cutoff = None if options["all"] else time.time() - options["since_days"] * 86400

        events = Event.objects.order_by("start").iterator()

        uploaded = 0
        for event in events:
            files = list(self._candidate_files(event, cutoff))
            if not files:
                continue

            event_folder_name = sanitize_name(
                f"{event.start.isoformat()} - {event.name}"
            )
            folder_id = existing_event_folders.get(event_folder_name)
            if folder_id is None:
                folder_id = get_or_create_folder(
                    service,
                    event_folder_name,
                    parent_id=root_id,
                )
                existing_event_folders[event_folder_name] = folder_id

            existing = get_existing_names(service, folder_id, [n for n, _ in files])
            for drive_name, path in files:
                if drive_name in existing:
                    continue
                logging.info(f"  Uploading: {event_folder_name}/{drive_name}")
                upload_file(service, folder_id, drive_name, path)
                uploaded += 1

        logging.info(f"Done. Uploaded: {uploaded}")

    def _candidate_files(self, event, cutoff):
        for kind, file_field in self._iter_event_files(event):
            try:
                path = file_field.path
                mtime = os.path.getmtime(path)
            except (FileNotFoundError, ValueError):
                continue
            if cutoff is not None and mtime <= cutoff:
                continue
            original = os.path.basename(file_field.name)
            drive_name = sanitize_name(f"{event.name} - {kind} - {original}")
            yield drive_name, path

    def _iter_event_files(self, event):
        if hasattr(event, "finance"):
            if event.finance.budget:
                yield "rozpočet", event.finance.budget
            for r in event.finance.receipts.all():
                if r.receipt:
                    yield "účtenka", r.receipt
        if hasattr(event, "propagation"):
            for img in event.propagation.images.all():
                if img.image:
                    yield "propagace", img.image
        if hasattr(event, "record"):
            for p in event.record.attendance_list_pages.all():
                if p.page:
                    yield "prezenčka", p.page
            for ph in event.record.photos.all():
                if ph.photo:
                    yield "fotka", ph.photo
