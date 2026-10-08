"""Switching the attendance mode must not carry participants over — a
simple-list participant may be anyone, and full-list exposes their profile."""

import pytest
from bis.helpers import paused_validation
from bis.models import User
from categories.models import EventGroupCategory
from event.models import EventRecord


@pytest.fixture
def event_url(event):
    return f"/api/frontend/events/{event.id}/"


@pytest.fixture
def participant(event):
    user = User.objects.create(
        first_name="Jan", last_name="Novák", email="jan.novak@example.com"
    )
    event.record.participants.add(user)
    return user


@pytest.mark.django_db
def test_switch_rejected_while_participants_remain(
    api_client, event_url, event, participant
):
    response = api_client.patch(
        event_url,
        {"record": {"attendance_list_type": "full-list"}},
        format="json",
    )

    assert response.status_code == 400
    event.record.refresh_from_db()
    assert (
        event.record.attendance_list_type == EventRecord.AttendanceListType.SIMPLE_LIST
    )


@pytest.mark.django_db
def test_switch_rejected_when_participants_are_kept_in_the_same_patch(
    api_client, event_url, event, participant
):
    response = api_client.patch(
        event_url,
        {
            "record": {
                "attendance_list_type": "full-list",
                "participants": [str(participant.id)],
            }
        },
        format="json",
    )

    assert response.status_code == 400
    event.record.refresh_from_db()
    assert (
        event.record.attendance_list_type == EventRecord.AttendanceListType.SIMPLE_LIST
    )


@pytest.mark.django_db
def test_switch_clearing_participants_is_accepted(
    api_client, event_url, event, participant
):
    response = api_client.patch(
        event_url,
        {
            "record": {
                "attendance_list_type": "full-list",
                "participants": [],
                "number_of_participants": None,
                "number_of_participants_under_26": None,
            }
        },
        format="json",
    )

    assert response.status_code == 200, response.data
    event.record.refresh_from_db()
    assert event.record.attendance_list_type == EventRecord.AttendanceListType.FULL_LIST
    assert event.record.participants.count() == 0


@pytest.mark.django_db
def test_filling_type_on_untyped_record_keeps_participants(
    api_client, event_url, event, participant
):
    event.record.attendance_list_type = None
    event.record.save()

    response = api_client.patch(
        event_url,
        {
            "record": {
                "attendance_list_type": "full-list",
                "participants": [str(participant.id)],
            }
        },
        format="json",
    )

    assert response.status_code == 200, response.data
    event.record.refresh_from_db()
    assert event.record.attendance_list_type == EventRecord.AttendanceListType.FULL_LIST
    assert event.record.participants.count() == 1


@pytest.mark.django_db
def test_patching_other_record_fields_keeps_participants(
    api_client, event_url, event, participant
):
    response = api_client.patch(
        event_url,
        {"record": {"total_hours_worked": 3}},
        format="json",
    )

    assert response.status_code == 200, response.data
    assert event.record.participants.count() == 1


@pytest.fixture
def camp_group(db):
    return EventGroupCategory.objects.create(name="Tábor", slug="camp")


@pytest.mark.django_db
def test_other_event_record_starts_untyped(event):
    event.record.delete()

    record = EventRecord.objects.create(event=event)

    assert record.attendance_list_type is None


@pytest.mark.django_db
def test_camp_event_record_starts_full_list(event, camp_group):
    event.record.delete()
    event.group = camp_group
    with paused_validation():
        event.save()

    record = EventRecord.objects.create(event=event)

    assert record.attendance_list_type == EventRecord.AttendanceListType.FULL_LIST


@pytest.mark.django_db
def test_moving_untyped_event_to_camp_makes_it_full_list(event, camp_group):
    event.record.attendance_list_type = None
    event.record.save()

    event.group = camp_group
    with paused_validation():
        event.save()

    event.record.refresh_from_db()
    assert event.record.attendance_list_type == EventRecord.AttendanceListType.FULL_LIST
