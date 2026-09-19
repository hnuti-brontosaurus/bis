import logging
import os
import time
from collections import defaultdict

from bis.drive import (
    build_drive_service,
    event_folder_name,
    get_existing_names,
    get_or_create_folder,
    list_subfolders,
    program_folder_name,
    sanitize_name,
    upload_file,
)
from django.conf import settings
from django.core.management.base import BaseCommand
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
        if settings.ENVIRONMENT != "prod":
            return

        service = build_drive_service()

        root_id = get_or_create_folder(
            service,
            options["root_folder"],
            parent_id=settings.GOOGLE_SHARED_DRIVE_ID,
        )
        self.subfolders: dict[str, dict[str, str]] = {}

        cutoff = None if options["all"] else time.time() - options["since_days"] * 86400

        events = (
            Event.objects.filter(is_archived=False)
            .select_related("program", "location")
            .order_by("start")
            .iterator()
        )

        uploaded = 0
        for event in events:
            files_by_section = defaultdict(list)
            for section, drive_name, path in self._candidate_files(event, cutoff):
                files_by_section[section].append((drive_name, path))
            if not files_by_section:
                continue

            year = str(event.start.year)
            program = program_folder_name(event)
            folder_name = event_folder_name(event)

            year_id = self._subfolder(service, root_id, year)
            program_id = self._subfolder(service, year_id, program)
            event_id = self._subfolder(service, program_id, folder_name)

            for section, files in files_by_section.items():
                section_id = self._subfolder(service, event_id, section)
                existing = get_existing_names(
                    service, section_id, [name for name, _ in files]
                )
                for drive_name, path in files:
                    if drive_name in existing:
                        continue
                    logging.info(
                        f"  Uploading: {year}/{program}/{folder_name}/{section}/{drive_name}"
                    )
                    upload_file(service, section_id, drive_name, path)
                    uploaded += 1

        logging.info(f"Done. Uploaded: {uploaded}")

    def _subfolder(self, service, parent_id, name):
        if parent_id not in self.subfolders:
            self.subfolders[parent_id] = list_subfolders(service, parent_id)
        folder_id = self.subfolders[parent_id].get(name)
        if folder_id is None:
            folder_id = get_or_create_folder(service, name, parent_id=parent_id)
            self.subfolders[parent_id][name] = folder_id
        return folder_id

    def _candidate_files(self, event, cutoff):
        for section, kind, file_field in self._iter_event_files(event):
            try:
                path = file_field.path
                mtime = os.path.getmtime(path)
            except (FileNotFoundError, ValueError):
                continue
            if cutoff is not None and mtime <= cutoff:
                continue
            original = os.path.basename(file_field.name)
            drive_name = sanitize_name(f"{event.name} - {kind} - {original}")
            yield section, drive_name, path

    def _iter_event_files(self, event):
        if hasattr(event, "finance"):
            if event.finance.budget:
                yield "dokumentace", "rozpočet", event.finance.budget
            for receipt in event.finance.receipts.all():
                if receipt.receipt:
                    yield "dokumentace", "účtenka", receipt.receipt
        if hasattr(event, "propagation"):
            for image in event.propagation.images.all():
                if image.image:
                    yield "propagace", "propagace", image.image
        if hasattr(event, "record"):
            for page in event.record.attendance_list_pages.all():
                if page.page:
                    yield "dokumentace", "prezenčka", page.page
            for photo in event.record.photos.all():
                if photo.photo:
                    yield "fotky", "fotka", photo.photo
