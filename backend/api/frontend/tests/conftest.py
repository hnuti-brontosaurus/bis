from datetime import date

import pytest
from administration_units.models import BrontosaurusMovement
from bis.helpers import paused_validation
from bis.models import Location, User
from categories.models import (
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
    RoleCategory,
)
from django.core.cache import cache
from event.models import Event, EventRecord
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.fixture
def movement(db):
    # BrontosaurusMovement.get() caches the singleton outside the test
    # transaction, so the rolled-back row would otherwise be served to the
    # next test and its stale FKs would blow up
    cache.delete("brontosaurus_movement")
    # User.update_roles() is a no-op without the movement singleton, and
    # without roles the API rejects every organizer
    for slug in ("organizer", "main_organizer"):
        RoleCategory.objects.get_or_create(slug=slug, defaults={"name": slug})
    director = User.objects.create(
        first_name="Ředitel", last_name="Hnutí", email="director@example.com"
    )
    yield BrontosaurusMovement.objects.create(
        director=director, finance_director=director
    )
    cache.delete("brontosaurus_movement")


@pytest.fixture
def organizer(movement):
    return User.objects.create(
        first_name="Orga",
        last_name="Nizer",
        email="organizer@example.com",
        birthday=date(1990, 1, 1),
    )


@pytest.fixture
def event(organizer):
    # Event.clean() demands a qualified main organizer and a located venue,
    # neither of which this endpoint cares about
    with paused_validation():
        event = Event.objects.create(
            name="Test event",
            start=date(2024, 5, 1),
            end=date(2024, 5, 2),
            location=Location.objects.create(name="Online"),
            group=EventGroupCategory.objects.create(name="Ostatní", slug="other"),
            category=EventCategory.objects.create(
                name="Dobrovolnická", slug="public__volunteering"
            ),
            program=EventProgramCategory.objects.create(name="Příroda", slug="nature"),
            intended_for=EventIntendedForCategory.objects.create(
                name="Pro všechny", slug="for_all"
            ),
            main_organizer=organizer,
        )
    event.other_organizers.add(organizer)
    organizer.update_roles()
    EventRecord.objects.create(
        event=event,
        attendance_list_type=EventRecord.AttendanceListType.SIMPLE_LIST,
    )
    return event


@pytest.fixture
def participants_url(event):
    return f"/api/frontend/events/{event.id}/record/participants/"


def authenticated_client(user):
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def api_client(organizer):
    return authenticated_client(organizer)


@pytest.fixture
def stranger_client(movement):
    return authenticated_client(
        User.objects.create(
            first_name="Cizí", last_name="Člověk", email="stranger@example.com"
        )
    )
