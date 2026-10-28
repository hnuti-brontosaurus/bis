import pytest
from bis.models import User
from event.models import EventRecord

PREFERENCES = {"subscription_status": 2, "do_not_call": True, "do_not_solicit": True}


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
