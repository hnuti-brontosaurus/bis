from datetime import date

import pytest
from nest_boxes.boxes import season_state_counts
from nest_boxes.models import Check, NestBox, SeasonState
from nest_boxes.statistics import season_statistics
from nest_boxes.tests.conftest import made_at, near

Status = NestBox.Status
Found, Cleaning, BoxLeft = Check.Found, Check.Cleaning, Check.BoxLeft


@pytest.fixture(autouse=True)
def season(monkeypatch):
    monkeypatch.setattr(Check, "current_season", staticmethod(lambda: 2025))
    return 2025


def check(box, season=2025, **kwargs):
    defaults = dict(
        found=Found.FOUND,
        cleaning=Cleaning.CLEANED,
        contents=[Check.Content.NOTHING],
        is_confirmed=True,
    )
    return Check.objects.create(
        box=box,
        date=date(season, 11, 1),
        made_at=made_at(8),
        **(defaults | kwargs),
    )


def states():
    return dict(NestBox.objects.with_season_state().values_list("name", "season_state"))


@pytest.fixture
def box(make_box):
    counter = iter(range(1, 100))

    def make(name, **kwargs):
        return make_box(name, location=near(east=next(counter) * 100), **kwargs)

    return make


def test_status(box, types):
    box("planned", status=Status.PLANNED, installed_on=None)
    box("to check")
    box("checked last season")
    check(NestBox.objects.get(name="checked last season"), season=2024)
    box("missing", status=Status.MISSING)
    box("taken down", status=Status.TAKEN_DOWN)
    box("needs repair", status=Status.NEEDS_REPAIR)
    box("needs replacing", status=Status.NEEDS_REPLACING)
    box("bats", type=types["netopyrnik"])
    box("ended", status=Status.ENDED, ended_on=date(2025, 8, 1))

    assert states() == {
        "planned": SeasonState.PLANNED,
        "to check": SeasonState.TO_CHECK,
        "checked last season": SeasonState.TO_CHECK,
        "missing": SeasonState.ATTENTION,
        "taken down": SeasonState.ATTENTION,
        "needs repair": SeasonState.ATTENTION,
        "needs replacing": SeasonState.ATTENTION,
        "bats": SeasonState.DONE,
        "ended": None,
    }


def test_confirmed_checks(box):
    check(box("cleaned"))
    check(box("not cleaned"), cleaning=Cleaning.NOT_CLEANED)
    check(box("not reached"), found=Found.NOT_REACHED, cleaning="")
    # Confirming applied the check; the box has been repaired since
    check(box("repaired"), box_left=BoxLeft.NEEDS_REPAIR)

    assert states() == {
        "cleaned": SeasonState.DONE,
        "not cleaned": SeasonState.ATTENTION,
        "not reached": SeasonState.TO_CHECK,
        "repaired": SeasonState.DONE,
    }


def test_pending_checks_count_as_confirmed(box):
    check(box("fine"), is_confirmed=False)
    check(
        box("found again", status=Status.MISSING),
        is_confirmed=False,
        box_left=BoxLeft.FINE,
    )
    check(
        box("mended", status=Status.NEEDS_REPAIR),
        is_confirmed=False,
        box_left=BoxLeft.FINE,
    )
    check(
        box("still broken", status=Status.NEEDS_REPAIR),
        is_confirmed=False,
        box_left="",
    )
    check(box("lost"), is_confirmed=False, found=Found.NOT_FOUND, cleaning="")
    check(box("broken"), is_confirmed=False, box_left=BoxLeft.NEEDS_REPLACING)
    check(box("taken down"), is_confirmed=False, box_left=BoxLeft.TAKEN_DOWN)
    check(
        box("hung", status=Status.PLANNED, installed_on=None),
        is_confirmed=False,
        cleaning="",
        box_changes={"hung": True},
    )

    assert states() == {
        "fine": SeasonState.DONE,
        "found again": SeasonState.DONE,
        "mended": SeasonState.DONE,
        "still broken": SeasonState.ATTENTION,
        "lost": SeasonState.ATTENTION,
        "broken": SeasonState.ATTENTION,
        "taken down": SeasonState.ATTENTION,
        "hung": SeasonState.DONE,
    }


def test_should_be_moved_needs_attention_even_when_cleaned(make_box):
    check(make_box("1", verified=True))
    make_box("2", location=near(east=3), verified=True)

    assert states() == {"1": SeasonState.ATTENTION, "2": SeasonState.ATTENTION}


def test_counts_per_area(area, box):
    box("planned", status=Status.PLANNED, installed_on=None)
    box("to check")
    check(box("done"))
    box("ended", status=Status.ENDED)

    assert season_state_counts(NestBox.objects.with_season_state()) == [
        {"area_id": area.pk, "planned": 1, "to_check": 1, "attention": 0, "done": 1}
    ]


def test_statistics_pie_of_the_current_season_is_the_season_states(area, box):
    check(box("pending"), is_confirmed=False)
    box("missing", status=Status.MISSING)
    box("to check")

    total = season_statistics(2025)["total"]

    assert (total["boxes"], total["done"], total["attention"]) == (3, 1, 1)
