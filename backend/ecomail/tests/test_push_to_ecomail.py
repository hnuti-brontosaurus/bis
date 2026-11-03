import pytest
from bis import signals
from bis.models import User

Status = User.SubscriptionStatus


@pytest.fixture
def pushes(db, monkeypatch):
    pushes = []

    def bulk_subscribe(session, list_id, users, resubscribe=False):
        pushes.extend((user.subscription_status, resubscribe) for user in users)

    monkeypatch.setattr(signals, "bulk_subscribe", bulk_subscribe)
    monkeypatch.setattr(signals, "get_session", lambda: None)
    return pushes


@pytest.fixture
def user(pushes):
    user = User.objects.create(
        email="a@example.com",
        first_name="A",
        last_name="B",
        subscription_status=Status.UNSUBSCRIBED,
    )
    pushes.clear()
    return user


def test_new_user_is_not_resubscribed(pushes):
    User.objects.create(email="a@example.com", first_name="A", last_name="B")

    assert pushes == [(Status.SUBSCRIBED, False)]


def test_subscribing_in_bis_resubscribes(user, pushes):
    user.subscription_status = Status.SUBSCRIBED
    user.save()

    assert pushes == [(Status.SUBSCRIBED, True)]


def test_unsubscribing_does_not_resubscribe(user, pushes):
    user.subscription_status = Status.SUBSCRIBED
    user.save()
    pushes.clear()

    user.subscription_status = Status.UNSUBSCRIBED
    user.save()

    assert pushes == [(Status.UNSUBSCRIBED, False)]


def test_unchanged_status_is_not_pushed(user, pushes):
    user.first_name = "C"
    user.save()

    assert pushes == []
