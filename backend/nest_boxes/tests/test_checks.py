from datetime import date
from uuid import uuid4

import pytest
from categories.models import NestBoxOccupant
from django.core.exceptions import PermissionDenied, ValidationError
from nest_boxes.checks import (
    BatchClosed,
    close_batch,
    confirm_batch,
    confirm_check,
    delete_check,
    parse_box_changes,
    submit_box,
    submit_check,
    upsert_check,
)
from nest_boxes.models import Check, NestBox
from nest_boxes.tests.conftest import ORIGIN, made_at, near


def new_check(box, hour, **kwargs):
    defaults = dict(
        date=date(2025, 11, 1),
        found=Check.Found.FOUND,
        cleaning=Check.Cleaning.CLEANED,
        contents=[Check.Content.BIRD_NEST],
    )
    return Check(box=box, made_at=made_at(hour), **(defaults | kwargs))


def geojson(point):
    return {"type": "Point", "coordinates": list(point.coords)}


@pytest.fixture
def box(batch):
    return batch.boxes.get()


@pytest.fixture
def occupants():
    return list(NestBoxOccupant.objects.filter(slug__in=["konadra", "vosy"]))


def test_the_check_made_later_wins(box, occupants):
    first = upsert_check(new_check(box, 10), occupants)
    assert upsert_check(new_check(box, 9), []) == first

    later = upsert_check(new_check(box, 11, note="later"), [])
    assert later != first
    assert list(Check.objects.all()) == [later]


def test_resending_a_check_updates_it(box, occupants):
    check = upsert_check(new_check(box, 10), occupants)
    resend = new_check(box, 10, note="edited")
    resend.pk = check.pk

    upsert_check(resend, occupants[:1])

    stored = Check.objects.get()
    assert stored.note == "edited"
    assert list(stored.occupants.all()) == occupants[:1]


def test_a_confirmed_check_is_never_replaced(box, manager):
    confirmed = upsert_check(new_check(box, 10), [])
    confirm_check(confirmed, manager)

    assert upsert_check(new_check(box, 11), []) == confirmed
    resend = new_check(box, 12, note="edited")
    resend.pk = confirmed.pk
    upsert_check(resend, [])
    assert Check.objects.get().note == ""


def test_batch_link_rules(batch, box, make_box, manager):
    check = submit_check(batch, new_check(box, 10, is_confirmed=True), [])
    assert check.batch == batch
    assert not check.is_confirmed
    assert check.cleaned_by == batch.cleaned_by

    with pytest.raises(PermissionDenied):
        submit_check(batch, new_check(make_box("not in batch"), 10), [])

    close_batch(batch)
    with pytest.raises(BatchClosed):
        submit_check(batch, new_check(box, 11), [])
    assert not Check.objects.get().is_confirmed


def test_confirming_applies_box_changes_and_verifies(box, manager, types):
    check = new_check(
        box,
        10,
        box_left=Check.BoxLeft.NEEDS_REPAIR,
        box_changes={
            "name": "1",
            "location": geojson(near(east=3)),
            "hole_shape": "round",
            "hole_size": 28,
            "type": types["maly_sykornik"].pk,
            "opening": "roof",
        },
    )
    upsert_check(check, [])
    confirm_check(check, manager)

    box = NestBox.objects.with_is_verified().get(pk=box.pk)
    assert box.is_verified
    assert box.condition == NestBox.Condition.NEEDS_REPAIR
    assert box.type == types["maly_sykornik"]
    assert box.opening == "roof"
    assert box.location.distance(near(east=3)) == pytest.approx(0)
    history = box.history.get()
    assert history.box_check == check
    assert history.date == check.date
    assert set(history.changes) == {
        "condition",
        "location",
        "hole_size",
        "type",
        "opening",
    }


def test_only_a_confirmed_check_from_the_field_verifies(box, manager):
    def is_verified():
        return NestBox.objects.with_is_verified().get(pk=box.pk).is_verified

    upsert_check(new_check(box, 10, date=date(2024, 11, 1), is_historical=True), [])
    check = upsert_check(new_check(box, 10), [])
    assert not is_verified()

    confirm_check(check, manager)
    assert is_verified()


@pytest.mark.parametrize(
    "found, box_left, status",
    [
        (Check.Found.NOT_FOUND, "", NestBox.Status.MISSING),
        (Check.Found.NOT_REACHED, "", NestBox.Status.IN_USE),
        (Check.Found.FOUND, Check.BoxLeft.TAKEN_DOWN, NestBox.Status.TAKEN_DOWN),
    ],
)
def test_check_sets_the_box_status(box, manager, found, box_left, status):
    check = upsert_check(new_check(box, 10, found=found, box_left=box_left), [])
    confirm_check(check, manager)
    box.refresh_from_db()
    assert box.status == status


def test_a_found_missing_box_is_back_in_use(make_box, manager):
    box = make_box(status=NestBox.Status.MISSING)
    confirm_check(upsert_check(new_check(box, 10), []), manager)
    box.refresh_from_db()
    assert box.status == NestBox.Status.IN_USE


def test_hanging_a_planned_box(make_box, manager):
    box = make_box(status=NestBox.Status.PLANNED, installed_on=None, planned_radius=20)
    check = upsert_check(new_check(box, 10, box_changes={"hung": True}), [])
    confirm_check(check, manager)
    box.refresh_from_db()
    assert box.status == NestBox.Status.IN_USE
    assert box.installed_on == check.date


@pytest.mark.parametrize(
    "box_changes",
    [
        {"colour": "red"},
        {"hole_shape": "square"},
        {"hole_size": "wide"},
        {"type": 999_999},
        {"name": ""},
        {"location": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}},
        {"location": "nowhere"},
        {"installed_on": "yesterday"},
        {"hung": "yes"},
    ],
)
def test_invalid_box_changes_are_rejected(box_changes):
    with pytest.raises(ValidationError):
        parse_box_changes(box_changes)


NEW_BOX = dict(
    name="new",
    location=near(north=100),
    hole_shape="open_front",
    opening="front",
    installed_on=date(2025, 11, 1),
)


@pytest.fixture
def new_box(types):
    def make(**kwargs):
        return {"id": uuid4(), "type": types["polobudka"], **NEW_BOX, **kwargs}

    return make


def hung_check(hour=10):
    return Check(id=uuid4(), date=date(2025, 11, 1), made_at=made_at(hour))


def test_a_volunteer_hangs_a_new_box(batch, make_box, new_box):
    values, check = new_box(), hung_check()
    box, stored = submit_box(batch, values, check)

    assert box.status == NestBox.Status.PLANNED and box.area == batch.area
    assert batch.boxes.filter(pk=box.pk).exists()
    assert (stored.box, stored.batch, stored.is_confirmed) == (box, batch, False)
    assert stored.box_changes["hung"] and stored.box_changes["name"] == "new"
    assert stored.contents == [Check.Content.NOTHING]

    resend = hung_check(11)
    resend.pk = check.pk
    submit_box(batch, values | {"note": "edited offline"}, resend)
    assert NestBox.objects.get(pk=box.pk).note == "edited offline"
    assert Check.objects.filter(box=box).count() == 1

    existing = make_box("existing", location=ORIGIN)
    with pytest.raises(PermissionDenied):
        submit_box(batch, new_box(id=existing.pk), hung_check())
    with pytest.raises(ValidationError):
        submit_box(batch, new_box(opening=""), hung_check())


def test_confirming_the_check_hangs_the_new_box(batch, box, manager, new_box):
    new, _ = submit_box(batch, new_box(), hung_check())
    submit_check(batch, new_check(box, 10, found=Check.Found.NOT_FOUND), [])

    confirm_batch(batch, manager)

    assert batch.closed_at and batch.confirmed_by == manager
    assert not Check.objects.filter(is_confirmed=False).exists()
    new = NestBox.objects.with_is_verified().get(pk=new.pk)
    assert new.status == NestBox.Status.IN_USE and new.is_verified
    assert NestBox.objects.get(pk=box.pk).status == NestBox.Status.MISSING
    with pytest.raises(BatchClosed):
        submit_check(batch, new_check(box, 11), [])


def test_deleting_the_check_deletes_the_new_box(batch, make_box, manager, new_box):
    new, check = submit_box(batch, new_box(), hung_check())
    delete_check(check)
    assert not NestBox.objects.filter(pk=new.pk).exists()

    planned = make_box("P", status=NestBox.Status.PLANNED, created_by=manager)
    batch.boxes.add(planned)
    delete_check(submit_check(batch, new_check(planned, 10), []))
    assert NestBox.objects.filter(pk=planned.pk).exists()
