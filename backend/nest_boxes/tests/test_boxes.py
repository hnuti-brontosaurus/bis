from datetime import date

import pytest
from categories.models import NestBoxType
from django.core.exceptions import ValidationError
from nest_boxes.boxes import (
    delete_box,
    duplicate_names,
    end_box,
    spacing_warnings,
    suggest_type,
    suggested_batch_boxes,
    update_box,
)
from nest_boxes.models import Batch, Check, NestBox
from nest_boxes.tests.conftest import made_at, near

Shape = NestBoxType.HoleShape


@pytest.mark.parametrize(
    "shape, size, slug",
    [
        (Shape.ROUND, 26, None),
        (Shape.ROUND, 27, "maly_sykornik"),
        (Shape.ROUND, 30, "maly_sykornik"),
        (Shape.ROUND, 32, "velky_sykornik"),
        (Shape.ROUND, 44, "velky_sykornik"),
        (Shape.ROUND, 45, "spackovnik"),
        (Shape.ROUND, 79, "kavkovnik"),
        (Shape.ROUND, 120, "doupnak"),
        (Shape.ROUND, 140, "sovinec"),
        (Shape.ROUND, None, None),
        (Shape.OVAL, None, "lejskovnik"),
        (Shape.OVAL, 30, "lejskovnik"),
        (Shape.OPEN_FRONT, None, "polobudka"),
        (Shape.SLIT, None, None),
        ("", None, None),
    ],
)
def test_type_is_suggested_from_the_hole(shape, size, slug):
    suggestion = suggest_type(shape, size)
    assert (suggestion and suggestion.slug) == slug


def test_netopyrnik_needs_no_cleaning(types):
    assert [slug for slug, t in types.items() if not t.needs_cleaning] == ["netopyrnik"]


def test_update_box_records_history(make_box, manager, types):
    box = make_box()
    changes = update_box(
        box,
        {"name": "1", "type": types["maly_sykornik"], "location": near(east=5)},
        manager,
        date(2025, 10, 1),
    )

    assert set(changes) == {"type", "location"}
    entry = box.history.get()
    assert entry.user == manager
    assert entry.changes["type"] == [
        types["velky_sykornik"].pk,
        types["maly_sykornik"].pk,
    ]
    assert entry.changes["location"][1] == pytest.approx(list(near(east=5).coords))


def test_update_box_without_changes_writes_no_history(make_box, manager):
    box = make_box()
    assert update_box(box, {"name": "1"}, manager, date(2025, 10, 1)) == {}
    assert not box.history.exists()


def test_end_and_delete(make_box, manager):
    box = make_box()
    with pytest.raises(ValidationError):
        delete_box(box)

    end_box(box, None, date(2025, 10, 1), manager)
    assert box.status == NestBox.Status.ENDED
    assert box.ended_on == date(2025, 10, 1)

    planned = make_box("2", status=NestBox.Status.PLANNED)
    delete_box(planned)
    assert not NestBox.objects.filter(pk=planned.pk).exists()


def test_spacing_warnings_for_placing(area, make_box, types):
    make_box("same, 40 m", location=near(east=40))
    make_box("same, 60 m", location=near(east=60))
    make_box("other, 10 m", location=near(north=10), type=types["maly_sykornik"])
    make_box("other, 20 m", location=near(north=20), type=types["maly_sykornik"])
    make_box("same, ended", location=near(east=1), status=NestBox.Status.ENDED)

    warnings = spacing_warnings(area, near(), types["velky_sykornik"])
    assert [(w.box.name, w.is_same_type, w.should_be_moved) for w in warnings] == [
        ("other, 10 m", False, False),
        ("same, 40 m", True, False),
    ]
    assert warnings[0].distance == pytest.approx(10, abs=0.5)

    close = make_box("same, 3 m", location=near(east=3))
    warnings = spacing_warnings(area, near(), types["velky_sykornik"])
    assert warnings[0].box == close and warnings[0].should_be_moved
    assert close not in [
        w.box for w in spacing_warnings(area, near(), None, exclude_id=close.pk)
    ]
    assert [w.box.name for w in spacing_warnings(area, near(), None)] == [
        "same, 3 m",
        "other, 10 m",
    ]


def test_duplicate_names_among_boxes_in_use(area, make_box, unit):
    box = make_box("A12")
    make_box("a12 ", location=near(east=100), status=NestBox.Status.ENDED)

    assert list(duplicate_names(area, " a12")) == [box]
    assert not duplicate_names(area, "A12", exclude_id=box.pk).exists()


def test_suggested_batch_boxes(area, make_box):
    checked = make_box("checked")
    Check.objects.create(
        box=checked,
        date=date(2025, 10, 1),
        made_at=made_at(8),
        found="found",
        contents=[],
        is_confirmed=True,
    )
    in_open_batch = make_box("in open batch")
    Batch.objects.create(area=area, name="open").boxes.add(in_open_batch)
    free = make_box("free")
    make_box("ended", status=NestBox.Status.ENDED)

    assert list(suggested_batch_boxes(area, 2025)) == [free]
