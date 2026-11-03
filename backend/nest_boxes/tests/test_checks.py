from datetime import date

import pytest
from categories.models import NestBoxOccupant
from django.core.exceptions import PermissionDenied, ValidationError
from nest_boxes.checks import (
    BatchClosed,
    close_batch,
    confirm_batch,
    confirm_check,
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

    box.refresh_from_db()
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
        "is_verified",
    }


def test_partial_changes_do_not_verify(box, manager):
    check = upsert_check(new_check(box, 10, box_changes={"hole_size": 34}), [])
    confirm_check(check, manager)
    box.refresh_from_db()
    assert box.hole_size == 34
    assert not box.is_verified


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


def test_a_volunteer_adds_a_box(batch, manager, make_box, types):
    box = NestBox(
        name="new",
        location=near(north=100),
        type=types["polobudka"],
        hole_shape="open_front",
        opening="front",
        installed_on=date(2025, 11, 1),
    )
    submit_box(batch, box)
    assert batch.boxes.filter(pk=box.pk).exists()
    assert box.area == batch.area
    assert not box.is_confirmed and not box.is_verified

    box.note = "edited offline"
    submit_box(batch, box)
    assert NestBox.objects.get(pk=box.pk).note == "edited offline"

    with pytest.raises(PermissionDenied):
        submit_box(batch, make_box("existing", location=ORIGIN))


def test_confirming_a_batch(batch, box, manager, types):
    new_box = submit_box(
        batch,
        NestBox(
            name="new",
            location=near(north=100),
            type=types["polobudka"],
            hole_shape="open_front",
            opening="front",
            installed_on=date(2025, 11, 1),
        ),
    )
    submit_check(batch, new_check(box, 10, found=Check.Found.NOT_FOUND), [])
    submit_check(batch, new_check(new_box, 10), [])

    confirm_batch(batch, manager)

    assert batch.closed_at and batch.confirmed_by == manager
    assert not Check.objects.filter(is_confirmed=False).exists()
    assert NestBox.objects.get(pk=new_box.pk).is_confirmed
    assert NestBox.objects.get(pk=box.pk).status == NestBox.Status.MISSING
    with pytest.raises(BatchClosed):
        submit_check(batch, new_check(box, 11), [])


def test_a_batch_with_an_incomplete_new_box_does_not_confirm(batch, manager):
    submit_box(batch, NestBox(name="new", location=near(north=100)))
    with pytest.raises(ValidationError):
        confirm_batch(batch, manager)
    assert batch.closed_at is None
