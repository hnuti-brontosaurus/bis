"""The simple-list attendance flow: participants are real Users, created and
linked through the nested participants endpoint."""

import pytest
from bis.models import User
from event.models import EventRecord


@pytest.mark.django_db
def test_create_links_new_user_to_event(api_client, participants_url, event):
    response = api_client.post(
        participants_url,
        {
            "first_name": "Jan",
            "last_name": "Novák",
            "email": "jan.novak@example.com",
            "phone": "",
        },
        format="json",
    )

    assert response.status_code == 201, response.data
    user = User.objects.get(email="jan.novak@example.com")
    assert list(event.record.participants.all()) == [user]
    assert not user.has_usable_password()


@pytest.mark.django_db
def test_create_dedupes_by_email(api_client, participants_url, event):
    payload = {
        "first_name": "Jan",
        "last_name": "Novák",
        "email": "jan.novak@example.com",
    }
    api_client.post(participants_url, payload, format="json")
    response = api_client.post(participants_url, payload, format="json")

    assert response.status_code == 201, response.data
    assert User.objects.filter(email="jan.novak@example.com").count() == 1
    assert event.record.participants.count() == 1


@pytest.mark.django_db
def test_create_rejects_invalid_email(api_client, participants_url):
    response = api_client.post(
        participants_url,
        {"first_name": "Jan", "last_name": "Novák", "email": "not-an-email"},
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.data


@pytest.mark.django_db
def test_create_rejected_on_non_simple_list_event(api_client, participants_url, event):
    event.record.attendance_list_type = EventRecord.AttendanceListType.FULL_LIST
    event.record.save()

    response = api_client.post(
        participants_url,
        {"first_name": "Jan", "last_name": "Novák", "email": "jan.novak@example.com"},
        format="json",
    )

    assert response.status_code == 400
    assert not User.objects.filter(email="jan.novak@example.com").exists()


@pytest.mark.django_db
def test_create_rejected_for_non_organizer(stranger_client, participants_url):
    response = stranger_client.post(
        participants_url,
        {"first_name": "Jan", "last_name": "Novák", "email": "jan.novak@example.com"},
        format="json",
    )

    assert response.status_code == 403
    assert not User.objects.filter(email="jan.novak@example.com").exists()


@pytest.mark.django_db
def test_destroy_unlinks_but_keeps_the_user(api_client, participants_url, event):
    created = api_client.post(
        participants_url,
        {"first_name": "Jan", "last_name": "Novák", "email": "jan.novak@example.com"},
        format="json",
    )

    response = api_client.delete(f"{participants_url}{created.data['id']}/")

    assert response.status_code == 204, response.data
    assert event.record.participants.count() == 0
    assert User.objects.filter(email="jan.novak@example.com").exists()


@pytest.mark.django_db
def test_list_masks_users_the_organizer_cannot_otherwise_see(
    api_client, participants_url, event
):
    invisible = User.objects.create(
        first_name="Neviditelný",
        last_name="Uživatel",
        email="invisible@example.com",
        phone="+420761001000",
    )
    event.record.participants.add(invisible)

    response = api_client.get(participants_url)

    assert response.status_code == 200, response.data
    row = response.data["results"][0]
    assert row["email"] == "invisible@example.com"
    assert row["first_name"] == ""
    assert row["last_name"] == ""
    assert row["phone"] == ""
