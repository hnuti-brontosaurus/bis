from datetime import timedelta

import pytest
from bis import emails
from bis.models import User
from django.utils import timezone
from event.models import EventRecord

PREFERENCES = {
    "subscription_status": 2,
    "do_not_call": True,
    "do_not_solicit": True,
    "do_not_send_after_event_email": True,
}


@pytest.fixture
def participant(event):
    participant = User.objects.create(
        first_name="Účast", last_name="Ník", email="participant@example.com"
    )
    # Organizers see the participants of full attendance lists only.
    event.record.attendance_list_type = EventRecord.AttendanceListType.FULL_LIST
    event.record.save()
    event.record.participants.add(participant)
    return participant


def user_url(user):
    return f"/api/frontend/users/{user.id}/"


@pytest.mark.django_db
def test_user_reads_and_changes_own_preferences(api_client, organizer):
    response = api_client.patch(user_url(organizer), PREFERENCES, format="json")

    assert response.status_code == 200, response.data
    assert {key: response.data[key] for key in PREFERENCES} == PREFERENCES
    organizer.refresh_from_db()
    assert organizer.do_not_call and organizer.do_not_solicit
    assert organizer.subscription_status == 2


@pytest.mark.django_db
def test_organizer_neither_sees_nor_changes_participants_preferences(
    api_client, participant
):
    response = api_client.get(user_url(participant))
    assert response.status_code == 200, response.data
    assert not PREFERENCES.keys() & response.data.keys()

    response = api_client.patch(user_url(participant), PREFERENCES, format="json")

    assert response.status_code == 200, response.data
    participant.refresh_from_db()
    assert not participant.do_not_call and not participant.do_not_solicit
    assert participant.subscription_status == User.SubscriptionStatus.SUBSCRIBED


@pytest.mark.django_db
def test_after_event_email_skips_who_refused_it(event, participant, monkeypatch):
    refusing = User.objects.create(
        first_name="Od",
        last_name="Mítá",
        email="refusing@example.com",
        do_not_send_after_event_email=True,
    )
    event.record.participants.add(refusing)
    event.end = timezone.now().date() - timedelta(days=1)
    event.save()
    recipients = []
    monkeypatch.setattr(
        emails.ecomail,
        "send_email",
        lambda sender, template, to, **kwargs: recipients.extend(to),
    )

    emails.event_end_participants_notification(event)

    assert recipients == [participant.email]
    refusing.refresh_from_db()
    assert refusing.last_after_event_email is None
