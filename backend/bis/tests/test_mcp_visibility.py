import datetime

import pytest
from bis.models import Location, User
from categories.models import (
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
)
from django.test import RequestFactory
from event.models import Event


def make_user(email):
    return User.objects.create(
        email=email,
        first_name="Test",
        last_name="User",
        _str="Test User",
    )


def make_event(name):
    return Event.objects.create(
        name=name,
        start=datetime.date(2026, 1, 10),
        end=datetime.date(2026, 1, 11),
        duration=2,
        location=Location.objects.create(name="Test"),
        group=EventGroupCategory.objects.create(name="Akce", slug="weekend_event"),
        category=EventCategory.objects.create(
            name="Veřejné", slug="public__volunteering"
        ),
        program=EventProgramCategory.objects.create(name="Příroda", slug="nature"),
        intended_for=EventIntendedForCategory.objects.create(
            name="Pro všechny", slug="for_all"
        ),
    )


@pytest.fixture
def permitted_events(db):
    # project.urls pulls in api.urls, whose filters query the DB at import
    # time, so bis.mcp_schema must only be imported once the db fixture is
    # active.
    from bis.mcp_schema import _permitted_events

    return _permitted_events


def make_info(user):
    request = RequestFactory().get("/mcp")
    request.user = user
    return type("Info", (), {"context": {"request": request}})()


@pytest.mark.django_db
def test_is_bot_true_for_brontobot_email():
    assert make_user("brontosaurus.bot@gmail.com").is_bot


@pytest.mark.django_db
def test_is_bot_false_for_regular_user():
    assert not make_user("member@example.com").is_bot


@pytest.mark.django_db
def test_bot_user_sees_all_events(permitted_events):
    make_event("Some other event")

    bot = make_user("brontosaurus.bot@gmail.com")

    assert set(permitted_events(make_info(bot))) == set(Event.objects.all())


@pytest.mark.django_db
def test_regular_user_sees_only_permitted_events(permitted_events):
    make_event("Some other event")

    member = make_user("member@example.com")

    assert set(permitted_events(make_info(member))) == set()
