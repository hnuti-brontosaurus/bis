import json
import logging
import re
import time

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

_FORBIDDEN_NAME_CHARS = re.compile(r'[<>:"/\\|?*]')

ROOT_FOLDER_NAME = "BIS export"
SHARED_SUBFOLDER_NAME = "Sdílené"


def build_drive_service():
    credentials_info = json.loads(settings.GOOGLE_CREDENTIALS)
    credentials_info["private_key"] = credentials_info["private_key"].replace(
        "\\n", "\n"
    )
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    return build("drive", "v3", credentials=credentials)


def escape_drive_query(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def sanitize_name(s: str) -> str:
    return _FORBIDDEN_NAME_CHARS.sub("_", s).strip(" .")


def get_or_create_folder(service, name, parent_id):
    results = (
        service.files()
        .list(
            q=(
                f"name='{escape_drive_query(name)}' "
                f"and mimeType='application/vnd.google-apps.folder' "
                f"and '{parent_id}' in parents and trashed=false"
            ),
            driveId=settings.GOOGLE_SHARED_DRIVE_ID,
            corpora="drive",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields="files(id)",
        )
        .execute()
    )
    if files := results.get("files", []):
        return files[0]["id"]
    return (
        service.files()
        .create(
            body={
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id],
            },
            supportsAllDrives=True,
            fields="id",
        )
        .execute()["id"]
    )


def list_subfolders(service, parent_id):
    folders = {}
    page_token = None
    while True:
        response = (
            service.files()
            .list(
                q=(
                    f"mimeType='application/vnd.google-apps.folder' "
                    f"and '{parent_id}' in parents and trashed=false"
                ),
                driveId=settings.GOOGLE_SHARED_DRIVE_ID,
                corpora="drive",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                fields="nextPageToken, files(id, name)",
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )
        for f in response.get("files", []):
            folders[f["name"]] = f["id"]
        page_token = response.get("nextPageToken")
        if not page_token:
            return folders


def get_existing_names(service, folder_id, names):
    name_conditions = " or ".join(f"name='{escape_drive_query(n)}'" for n in names)
    q = f"({name_conditions}) and '{folder_id}' in parents and trashed=false"
    results = (
        service.files()
        .list(
            q=q,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            fields="files(name)",
        )
        .execute()
    )
    return {f["name"] for f in results.get("files", [])}


def event_folder_name(event):
    location = event.location.name if event.location else "bez lokality"
    return sanitize_name(f"{event.start.isoformat()} - {event.name} - {location}")


def get_or_create_shared_folder_url(event):
    if event.shared_folder_url:
        return event.shared_folder_url

    if settings.ENVIRONMENT != "prod":
        return None

    from event.models import Event

    service = build_drive_service()
    root_id = get_or_create_folder(
        service, ROOT_FOLDER_NAME, settings.GOOGLE_SHARED_DRIVE_ID
    )
    year_id = get_or_create_folder(service, str(event.start.year), root_id)
    event_folder_id = get_or_create_folder(service, event_folder_name(event), year_id)
    shared_id = get_or_create_folder(service, SHARED_SUBFOLDER_NAME, event_folder_id)

    service.permissions().create(
        fileId=shared_id,
        body={"type": "anyone", "role": "writer"},
        supportsAllDrives=True,
        fields="id",
    ).execute()

    url = f"https://drive.google.com/drive/folders/{shared_id}"
    Event.objects.filter(pk=event.pk).update(shared_folder_url=url)
    return url


def upload_file(service, folder_id, name, path):
    for attempt in range(5):
        try:
            service.files().create(
                body={"name": name, "parents": [folder_id]},
                media_body=MediaFileUpload(path, resumable=True),
                supportsAllDrives=True,
                fields="id",
            ).execute()
            return
        except Exception as e:
            if attempt == 4:
                raise
            logging.warning(
                f"  Upload failed (attempt {attempt + 1}/5): {e}, retrying..."
            )
            time.sleep(2**attempt)
