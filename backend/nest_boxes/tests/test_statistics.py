from datetime import date

import pytest
from nest_boxes.models import Check, NestBox
from nest_boxes.statistics import default_season, season_statistics
from nest_boxes.tests.conftest import made_at, near
from rest_framework.test import APIClient

Content = Check.Content


@pytest.fixture
def season_2026(monkeypatch):
    monkeypatch.setattr(Check, "current_season", staticmethod(lambda: 2026))


def check(box, contents, season=2025, **kwargs):
    return Check.objects.create(
        box=box,
        date=date(season, 11, 1),
        made_at=made_at(8),
        found=kwargs.pop("found", Check.Found.FOUND),
        cleaning=kwargs.pop("cleaning", Check.Cleaning.CLEANED),
        contents=contents,
        is_confirmed=kwargs.pop("is_confirmed", True),
        **kwargs,
    )


@pytest.fixture
def boxes(make_box, types):
    def box(name, **kwargs):
        return make_box(name, location=near(east=len(name) * 100), **kwargs)

    return {
        "bird": box("bird"),
        "wasps": box("wasps", condition=NestBox.Condition.NEEDS_REPAIR),
        "empty": box("empty"),
        "unknown": box("unknown"),
        "closed": box("closed"),
        "lost": box("lost"),
        "pending": box("pending"),
        "unchecked": box("unchecked"),
        "bats": box("bats", type=types["netopyrnik"]),
        "new": box("new", installed_on=date(2026, 7, 1)),
        "ended": box("ended", status=NestBox.Status.ENDED, ended_on=date(2025, 6, 30)),
        "ended_later": box(
            "ended later", status=NestBox.Status.ENDED, ended_on=date(2025, 12, 1)
        ),
        "planned": box("planned", status=NestBox.Status.PLANNED, installed_on=None),
    }


def test_season_statistics(area, boxes):
    check(boxes["bird"], [Content.BIRD_NEST])
    check(boxes["wasps"], [Content.OTHER_ANIMAL], cleaning=Check.Cleaning.NOT_CLEANED)
    check(boxes["empty"], [Content.NOTHING])
    check(boxes["unknown"], [Content.UNKNOWN])
    check(boxes["closed"], [], cleaning=Check.Cleaning.NOT_CLEANED)
    check(boxes["lost"], [], found=Check.Found.NOT_FOUND, cleaning="")
    check(boxes["pending"], [Content.BIRD_NEST], is_confirmed=False)
    check(boxes["bats"], [Content.OTHER_ANIMAL])
    check(boxes["bird"], [Content.BIRD_NEST], season=2024)
    check(boxes["empty"], [Content.NOTHING], season=2024)

    statistics = season_statistics(2025)

    expected = {
        "boxes": 9,
        "cleaned": 3,
        "inspected": 3,
        "occupied": 2,
        "bird_occupied": 1,
        "previous_inspected": 2,
        "previous_occupied": 1,
        # Past seasons take attention from what the checks reported
        "done": 3,
        "attention": 3,
    }
    assert statistics["areas"] == [{"area": area, **expected}]
    assert statistics["total"] == expected
    assert statistics["seasons"][-1] == 2024


def test_a_new_season_shows_once_anything_is_checked_in_it(season_2026, boxes):
    assert default_season() == 2025
    assert season_statistics(default_season())["seasons"] == [2026, 2025]

    check(boxes["bird"], [Content.BIRD_NEST])
    assert default_season() == 2025

    check(boxes["empty"], [Content.NOTHING], season=2026, is_confirmed=False)
    assert default_season() == 2026


def test_statistics_default_to_the_default_season(season_2026, boxes):
    check(boxes["bird"], [Content.BIRD_NEST])
    client = APIClient()

    statistics = client.get("/api/nest_boxes/public/statistics/").json()
    assert statistics["season"] == 2025
    assert statistics["seasons"] == [2026, 2025]
    assert statistics["total"]["cleaned"] == 1

    statistics = client.get("/api/nest_boxes/public/statistics/?season=2026").json()
    assert statistics["season"] == 2026
    assert statistics["total"]["cleaned"] == 0
