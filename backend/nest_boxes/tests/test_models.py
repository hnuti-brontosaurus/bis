from datetime import date

import pytest
from django.db import IntegrityError
from nest_boxes.models import Area, Check, NestBox
from nest_boxes.tests.conftest import made_at, near


@pytest.mark.parametrize(
    "day, season",
    [
        (date(2025, 7, 1), 2025),
        (date(2025, 12, 31), 2025),
        (date(2026, 6, 30), 2025),
        (date(2026, 7, 1), 2026),
    ],
)
def test_season_runs_from_july_to_june(day, season):
    assert Check.season_of(day) == season


def test_one_check_per_box_and_season(make_box):
    box = make_box()
    first = Check.objects.create(
        box=box, date=date(2025, 10, 1), made_at=made_at(8), found="found", contents=[]
    )
    assert first.season == 2025
    assert first.cleaned_by == box.area.administration_unit

    with pytest.raises(IntegrityError):
        Check.objects.create(
            box=box,
            date=date(2026, 3, 1),
            made_at=made_at(9),
            found="found",
            contents=[],
        )


def test_region_follows_location(make_box, region):
    box = make_box()
    assert box.region == region

    box.location = near(east=500_000)
    box.save()
    assert box.region is None


def distances():
    return {
        box.name: (box.closest_distance, box.closest_same_type_distance)
        for box in NestBox.objects.all()
    }


def test_distances_count_boxes_in_use_only(make_box, types):
    make_box("1")
    make_box("2", location=near(east=10))
    make_box("3", location=near(north=30), type=types["maly_sykornik"])
    make_box("4", location=near(east=1), status=NestBox.Status.ENDED)
    make_box("5", location=near(east=2), is_confirmed=False)

    result = distances()
    assert result["1"] == (pytest.approx(10, abs=0.5), pytest.approx(10, abs=0.5))
    assert result["2"] == (pytest.approx(10, abs=0.5), pytest.approx(10, abs=0.5))
    assert result["3"] == (pytest.approx(30, abs=0.5), None)
    assert result["4"] == (None, None)
    assert result["5"] == (None, None)


def test_distances_follow_moves_status_and_area(make_box, unit):
    first = make_box("1")
    second = make_box("2", location=near(east=10))

    second.location = near(east=40)
    second.save()
    first.refresh_from_db()
    assert first.closest_distance == pytest.approx(40, abs=0.5)

    second.area = Area.objects.create(name="Jinde", administration_unit=unit)
    second.save()
    first.refresh_from_db()
    assert first.closest_distance is None

    second.delete()
    first.refresh_from_db()
    assert first.closest_distance is None


def test_should_be_moved_waits_until_verified(make_box, types):
    make_box("1", is_verified=True)
    make_box("2", location=near(east=10), is_verified=False)
    make_box("3", location=near(east=200), is_verified=True)

    flags = dict(
        NestBox.objects.with_should_be_moved().values_list("name", "should_be_moved")
    )
    assert flags == {"1": True, "2": False, "3": False}


def test_area_marker_is_centroid_of_boxes_in_use(area, make_box):
    make_box("1")
    make_box("2", location=near(east=100))
    make_box("3", location=near(east=1000), status=NestBox.Status.ENDED)

    area = Area.objects.with_markers().get(pk=area.pk)
    assert area.box_count == 2
    assert area.marker.x == pytest.approx(near(east=50).x)
