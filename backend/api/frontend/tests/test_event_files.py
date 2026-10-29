"""The close-event form uploads each file as soon as it is picked, which can be
before the event has a record or finance to attach it to."""

import base64
import io

import pytest
from bis.models import User
from categories.models import RoleCategory
from event.models import EventFinance, EventRecord
from PIL import Image

from .conftest import authenticated_client


def _png():
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buffer, format="PNG")
    return (
        "data:image/png;filename=a;base64,"
        + base64.b64encode(buffer.getvalue()).decode()
    )


@pytest.fixture
def event_without_record(event):
    event.record.delete()
    event.refresh_from_db()
    return event


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path, field",
    [("record/photos", "photo"), ("record/attendance_list_pages", "page")],
)
def test_upload_creates_the_missing_record(
    api_client, event_without_record, path, field
):
    response = api_client.post(
        f"/api/frontend/events/{event_without_record.id}/{path}/",
        {field: _png()},
        format="json",
    )

    assert response.status_code == 201, response.data
    assert EventRecord.objects.filter(event=event_without_record).exists()


@pytest.mark.django_db
def test_receipt_upload_creates_the_missing_finance(api_client, event):
    response = api_client.post(
        f"/api/frontend/events/{event.id}/finance/receipts/",
        {"receipt": _png()},
        format="json",
    )

    assert response.status_code == 201, response.data
    assert EventFinance.objects.get(event=event).receipts.count() == 1


@pytest.mark.django_db
def test_organizer_of_another_event_cannot_upload(event_without_record):
    other_organizer = User.objects.create(
        first_name="Jiný", last_name="Organizátor", email="other@example.com"
    )
    other_organizer.roles.add(RoleCategory.objects.get(slug="organizer"))

    response = authenticated_client(other_organizer).post(
        f"/api/frontend/events/{event_without_record.id}/record/photos/",
        {"photo": _png()},
        format="json",
    )

    assert response.status_code == 403
    assert not EventRecord.objects.filter(event=event_without_record).exists()


@pytest.mark.django_db
def test_office_worker_uploads_to_an_event_they_do_not_organize(event_without_record):
    office_worker = User.objects.create(
        first_name="Kancl", last_name="Brontosaura", email="office@example.com"
    )
    office_worker.roles.add(
        RoleCategory.objects.get_or_create(
            slug="office_worker", defaults={"name": "office_worker"}
        )[0]
    )

    response = authenticated_client(office_worker).post(
        f"/api/frontend/events/{event_without_record.id}/record/photos/",
        {"photo": _png()},
        format="json",
    )

    assert response.status_code == 201, response.data


@pytest.mark.django_db
def test_organizer_cannot_upload_to_an_archived_event(api_client, event):
    event.is_archived = True
    event.save(update_fields=["is_archived"])

    response = api_client.post(
        f"/api/frontend/events/{event.id}/record/photos/",
        {"photo": _png()},
        format="json",
    )

    assert response.status_code == 403
