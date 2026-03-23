import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from event.models import Event


class Command(BaseCommand):
    help = (
        "Uploads all event files for 'Modrý Kámen' administration unit to Google Drive."
    )

    def handle(self, *args, **options):
        service = self._build_drive_service()
        folder_id = self._get_or_create_folder(service, "Modrý kámen export")
        logging.info(f"Using Drive folder id: {folder_id}")

        events = Event.objects.filter(
            administration_units__abbreviation="Modrý Kámen"
        ).distinct()
        logging.info(f"Found {events.count()} events")

        uploaded = 0
        for event in events:
            date_str = event.start.strftime("%Y-%m-%d") if event.start else "0000-00-00"
            for file_path in self._collect_files(event):
                drive_name = f"{date_str} - {event.name} - {file_path.name}"
                logging.info(f"  Uploading: {drive_name}")
                self._upload_file(service, folder_id, drive_name, file_path.path)
                uploaded += 1

        logging.info(f"Done. Uploaded: {uploaded}")

    def _build_drive_service(self):
        credentials_info = json.loads(settings.GOOGLE_CREDENTIALS)
        credentials_info["private_key"] = credentials_info["private_key"].replace(
            "\\n", "\n"
        )
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        return build("drive", "v3", credentials=credentials)

    def _get_or_create_folder(self, service, name):
        results = (
            service.files()
            .list(
                q=f"name='{name}' and mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false",
                fields="files(id)",
            )
            .execute()
        )
        if files := results.get("files", []):
            return files[0]["id"]
        return (
            service.files()
            .create(
                body={"name": name, "mimeType": "application/vnd.google-apps.folder"},
                fields="id",
            )
            .execute()["id"]
        )

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

    def _upload_file(self, service, folder_id, name, path):
        service.files().create(
            body={"name": name, "parents": [folder_id]},
            media_body=MediaFileUpload(path, resumable=True),
            fields="id",
        ).execute()
