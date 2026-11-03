import datetime
import itertools

import pytest
from bis.models import Location, User
from categories.models import (
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
)
from dateutil.relativedelta import relativedelta
from django.contrib.admin.sites import site
from django.db.models import F, Value
from django.db.models.lookups import GreaterThan
from django.test import RequestFactory
from event.models import Event, EventRecord, turns_27
from xlsx_export.serializers import EventExportSerializer

START = datetime.date(2026, 1, 10)


def legacy_counts(record):
    """The Python implementation the SQL one replaced, kept as the oracle."""
    people = {
        user.id: user
        for user in [*record.participants.all(), *record.event.other_organizers.all()]
    }.values()
    sub_events = record.event.number_of_sub_events
    count = record.number_of_participants or len(people) * sub_events
    under_26 = len(
        [
            p
            for p in people
            if p.birthday and relativedelta(record.event.start, p.birthday).years <= 26
        ]
    )
    young = record.number_of_participants_under_26 or under_26 * sub_events
    percentage = "0%" if not count else f"{int(young / count * 100)}%"
    return count, young, percentage


def is_young(start, birthday):
    return relativedelta(start, birthday).years <= 26


@pytest.mark.parametrize(
    "start",
    [
        datetime.date(2024, 2, 28),
        datetime.date(2024, 2, 29),
        datetime.date(2024, 3, 1),
        datetime.date(2025, 2, 28),
        datetime.date(2025, 3, 1),
        datetime.date(2026, 12, 31),
        START,
    ],
)
def test_age_matches_relativedelta_for_every_birthday_around_27(db, start):
    twenty_seventh = start - relativedelta(years=27)
    birthdays = [twenty_seventh + datetime.timedelta(days=d) for d in range(-800, 800)]
    birthdays += [start + datetime.timedelta(days=d) for d in range(-3, 30)]
    users = User.objects.bulk_create(
        User(email=f"{b}@example.com", first_name="B", last_name="D", birthday=b)
        for b in birthdays
    )

    young = set(
        User.objects.filter(pk__in=[u.pk for u in users])
        .filter(GreaterThan(turns_27(F("birthday")), Value(start)))
        .values_list("birthday", flat=True)
    )

    assert young == {b for b in birthdays if is_young(start, b)}


@pytest.fixture
def make_event(db):
    location = Location.objects.create(name="Test")
    categories = dict(
        group=EventGroupCategory.objects.create(name="Akce", slug="weekend_event"),
        category=EventCategory.objects.create(
            name="Veřejné", slug="public__volunteering"
        ),
        program=EventProgramCategory.objects.create(name="Příroda", slug="nature"),
        intended_for=EventIntendedForCategory.objects.create(
            name="Pro všechny", slug="for_all"
        ),
    )

    def make_event(number_of_sub_events=1):
        return Event.objects.create(
            name="Akce",
            start=START,
            end=START,
            duration=1,
            location=location,
            number_of_sub_events=number_of_sub_events,
            **categories,
        )

    return make_event


@pytest.fixture
def people(db):
    birthdays = {
        "young": datetime.date(2010, 5, 1),
        "old": datetime.date(1980, 5, 1),
        "unknown": None,
        "turns_27_on_start": START - relativedelta(years=27),
        "turns_27_day_after": START - relativedelta(years=27) + relativedelta(days=1),
    }
    return [
        User.objects.create(
            email=f"{name}@example.com", first_name=name, last_name="P", birthday=b
        )
        for name, b in birthdays.items()
    ]


ATTENDANCE = {
    "nobody": ([], []),
    "participants": (slice(0, 5), []),
    "organizers": ([], slice(0, 5)),
    "overlapping": (slice(0, 3), slice(1, 5)),
}


@pytest.mark.parametrize(
    "number_of_participants, number_of_participants_under_26, sub_events, attendance",
    itertools.product([None, 0, 100], [None, 0, 29], [1, 3], ATTENDANCE),
)
def test_counts_match_the_python_implementation(
    make_event,
    people,
    number_of_participants,
    number_of_participants_under_26,
    sub_events,
    attendance,
):
    # Everyone also attended and organized another event, so the joins
    # behind the SQL count meet each person more than once.
    other_event = make_event()
    EventRecord.objects.create(event=other_event).participants.set(people)
    other_event.other_organizers.set(people)

    event = make_event(number_of_sub_events=sub_events)
    record = EventRecord.objects.create(
        event=event,
        number_of_participants=number_of_participants,
        number_of_participants_under_26=number_of_participants_under_26,
    )
    participants, organizers = ATTENDANCE[attendance]
    record.participants.set(people[participants] if participants else [])
    event.other_organizers.set(people[organizers] if organizers else [])

    expected = legacy_counts(EventRecord.objects.get(pk=record.pk))

    fresh = EventRecord.objects.get(pk=record.pk)
    assert (
        fresh.get_participants_count(),
        fresh.get_young_participants_count(),
        fresh.get_young_percentage(),
    ) == expected

    annotated = EventRecord.objects.annotate(**EventRecord.participant_counts()).get(
        pk=record.pk
    )
    assert (
        annotated.get_participants_count(),
        annotated.get_young_participants_count(),
        annotated.get_young_percentage(),
    ) == expected

    exported = (
        EventExportSerializer.get_related(Event.objects.filter(pk=event.pk))
        .get()
        .record
    )
    assert (
        exported.get_participants_count(),
        exported.get_young_participants_count(),
        exported.get_young_percentage(),
    ) == expected

    request = RequestFactory().get("/admin/bis/event/")
    request.user = people[0]
    request.user.can_see_all = True
    request._is_changelist = True
    event_admin = site._registry[Event]
    row = event_admin.get_queryset(request).get(pk=event.pk)
    assert (
        event_admin.get_participants_count(row),
        event_admin.get_young_percentage(row),
    ) == (expected[0], expected[2])

    assert set(fresh.get_all_participants()) == {
        *fresh.participants.all(),
        *event.other_organizers.all(),
    }


def test_admin_shows_nothing_for_an_event_without_record(make_event, people):
    event = make_event()
    request = RequestFactory().get("/admin/bis/event/")
    request.user = people[0]
    request.user.can_see_all = True
    request._is_changelist = True
    event_admin = site._registry[Event]

    row = event_admin.get_queryset(request).get(pk=event.pk)

    assert event_admin.get_participants_count(row) is None
    assert event_admin.get_young_percentage(row) is None
