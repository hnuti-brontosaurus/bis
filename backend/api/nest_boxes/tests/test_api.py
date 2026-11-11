import base64
import io
import json
from datetime import date
from unittest.mock import patch
from uuid import uuid4

import pytest
from api.nest_boxes.tests.conftest import API
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from django.utils.timezone import now
from nest_boxes.checks import close_batch
from nest_boxes.models import Batch, Check, HelpArticle, NestBox
from nest_boxes.tests.conftest import made_at, near
from PIL import Image


def geojson(point):
    return {"type": "Point", "coordinates": list(point.coords)}


def link_check(box, hour=10, **kwargs):
    return {
        "id": str(uuid4()),
        "box_id": str(box.pk),
        "date": "2025-11-01",
        "made_at": made_at(hour).isoformat(),
        "found": "found",
        "cleaning": "cleaned",
        "contents": ["nothing"],
        "box_left": "fine",
        "volunteer_nickname": "Sýkorka",
        "volunteer_email": "sykorka@example.com",
    } | kwargs


NOT_FOUND = dict(
    found="not_found", cleaning="", contents=[], box_left="", note="není na stromě"
)


def contains_coordinates(data, point):
    return str(point.x)[:7] in json.dumps(data)


def test_public_areas_never_show_box_coordinates(anonymous, make_box, area):
    # One box would be its own marker, which the design accepts
    box = make_box(location=near(east=123, north=45))
    other = make_box("2", location=near(east=-200, north=-80))

    areas = anonymous.get(f"{API}/public/areas/").json()["results"]

    assert areas[0]["box_count"] == 2
    assert not contains_coordinates(areas, other.location)
    assert set(areas[0]) == {"id", "name", "administration_unit", "marker", "box_count"}
    statistics = anonymous.get(f"{API}/public/statistics/?season=2025").json()
    assert not contains_coordinates(areas, box.location)
    assert "location" not in json.dumps(statistics)


@pytest.mark.parametrize(
    "url",
    [
        "areas/",
        "areas/season_states/",
        "boxes/",
        "boxes/map/",
        "checks/",
        "batches/",
        "batches/open/",
    ],
)
def test_non_managers_are_refused(anonymous, client_for, stranger, area, url):
    assert anonymous.get(f"{API}/{url}").status_code == 403
    assert client_for(stranger).get(f"{API}/{url}").status_code == 403


def test_budkar_creates_areas(client_for, budkar, unit):
    response = client_for(budkar).post(
        f"{API}/areas/", {"name": "Nová", "administration_unit_id": unit.pk}
    )
    assert response.status_code == 201


def test_board_manages_the_units_areas_only(
    client_for, manager, unit, area, other_area, make_box
):
    unit.board_members.add(manager)
    client = client_for(manager)
    box = make_box()
    elsewhere = make_box("2", location=near(east=900), area=other_area)

    assert client.get(f"{API}/areas/{area.pk}/").status_code == 200
    assert client.get(f"{API}/areas/{other_area.pk}/").status_code == 404
    assert [row["id"] for row in client.get(f"{API}/boxes/map/").json()] == [
        str(box.pk)
    ]
    assert client.get(f"{API}/boxes/{elsewhere.pk}/").status_code == 404
    moved = client.patch(
        f"{API}/boxes/{box.pk}/", {"area_id": other_area.pk}, format="json"
    )
    assert moved.status_code == 403
    created = client.post(
        f"{API}/batches/", {"area_id": other_area.pk, "name": "X"}, format="json"
    )
    assert created.status_code == 403
    assert (
        client.patch(
            f"{API}/areas/{area.pk}/",
            {"administration_unit_id": other_area.administration_unit_id},
            format="json",
        ).status_code
        == 403
    )


def test_units_budkar_manages_and_creates_its_areas(
    client_for, manager, unit, other_unit
):
    unit.nest_box_managers.add(manager)
    client = client_for(manager)

    data = client.get(f"{API}/whoami/").json()
    assert data["is_manager"] and not data["is_budkar"]
    assert data["managed_unit_ids"] == [unit.pk]
    created = client.post(
        f"{API}/areas/", {"name": "Nová", "administration_unit_id": unit.pk}
    )
    assert created.status_code == 201
    refused = client.post(
        f"{API}/areas/", {"name": "Cizí", "administration_unit_id": other_unit.pk}
    )
    assert refused.status_code == 403
    assert client.get(f"{API}/whoami/").json()["managed_area_ids"] == [
        created.json()["id"]
    ]


def test_moving_a_box_leaves_its_open_batch(budkar_client, batch, other_area):
    box = batch.boxes.get()

    response = budkar_client.patch(
        f"{API}/boxes/{box.pk}/", {"area_id": other_area.pk}, format="json"
    )

    assert response.json()["area_id"] == other_area.pk
    assert not batch.boxes.exists()


def test_boxes_move_together(
    client_for, budkar_client, stranger, make_box, area, other_area
):
    first = make_box("1")
    second = make_box("2", location=near(east=100))
    make_box("2", location=near(east=900), area=other_area)
    url = f"{API}/boxes/move/"
    payload = {"box_ids": [str(first.pk), str(second.pk)], "area_id": other_area.pk}

    area.administration_unit.board_members.add(stranger)
    assert client_for(stranger).post(url, payload, format="json").status_code == 403
    response = budkar_client.post(url, payload, format="json").json()

    assert {box["area_id"] for box in response["boxes"]} == {other_area.pk}
    assert response["duplicate_names"] == ["2"]
    assert not area.boxes.exists()
    # Back is refused to the board, which doesn't manage the other unit's boxes
    back = {**payload, "area_id": area.pk}
    assert client_for(stranger).post(url, back, format="json").status_code == 400


def test_outlines_split_mingled_areas(budkar_client, make_box, area, other_area):
    for east in (0, 100, 200):
        make_box(str(east), location=near(east=east))
    make_box("J", location=near(east=300), area=other_area)
    make_box("far", location=near(north=5000), status=NestBox.Status.ENDED)

    outlines = {
        row["id"]: GEOSGeometry(json.dumps(row["outline"]))
        for row in budkar_client.get(f"{API}/areas/outlines/").json()
    }

    assert set(outlines) == {area.pk, other_area.pk}
    assert outlines[area.pk].contains(near(east=100))
    assert not outlines[area.pk].contains(near(east=300))
    assert outlines[other_area.pk].contains(near(east=300))
    assert outlines[area.pk].intersection(outlines[other_area.pk]).area < 1e-10


def test_whoami(anonymous, client_for, stranger, budkar_client, batch):
    assert anonymous.get(f"{API}/whoami/").json()["user"] is None
    data = budkar_client.get(f"{API}/whoami/").json()
    assert data["is_manager"]
    assert data["open_batch_count"] == 1
    data = client_for(stranger).get(f"{API}/whoami/").json()
    assert not data["is_manager"]
    assert data["open_batch_count"] == 0


def test_volunteer_sees_only_the_batchs_boxes(anonymous, batch, make_box, other_area):
    outside = make_box("2", location=near(east=300, north=200))
    elsewhere = make_box("3", location=near(east=900, north=700), area=other_area)
    make_box("4", location=near(east=600), status=NestBox.Status.ENDED)

    data = anonymous.get(f"{API}/links/{batch.token}/").json()

    assert [box["id"] for box in data["boxes"]] == [str(batch.boxes.get().pk)]
    # The unit's other boxes hanging, greyed out on the map
    assert data["other_boxes"] == [
        {"id": str(outside.pk), "name": "2", "location": geojson(outside.location)}
    ]
    assert not contains_coordinates(data, elsewhere.location)
    assert {"types", "occupants", "end_reasons", "not_cleaned_reasons"} == set(
        data["categories"]
    )
    assert len(data["help_articles"]) == len(HelpArticle.Slug)


def test_volunteer_cannot_check_a_box_outside_the_batch(anonymous, batch, make_box):
    outside = make_box("2", location=near(east=300))
    response = anonymous.post(
        f"{API}/links/{batch.token}/checks/", link_check(outside), format="json"
    )
    assert response.status_code == 403


def test_closed_link_is_gone(anonymous, batch):
    box = batch.boxes.get()
    close_batch(batch)

    assert anonymous.get(f"{API}/links/{batch.token}/").status_code == 410
    response = anonymous.post(
        f"{API}/links/{batch.token}/checks/", link_check(box), format="json"
    )
    assert response.status_code == 410
    assert not Check.objects.exists()


def test_unknown_link_is_not_found(anonymous):
    assert anonymous.get(f"{API}/links/{uuid4()}/").status_code == 404


def test_later_check_wins(anonymous, batch):
    box = batch.boxes.get()
    url = f"{API}/links/{batch.token}/checks/"

    late = anonymous.post(url, link_check(box, hour=12, note="pozdě"), format="json")
    early = anonymous.post(url, link_check(box, hour=9, note="brzy"), format="json")
    resend = anonymous.post(
        url, late.json()["check"] | {"volunteer_email": "a@b.cz"}, format="json"
    )

    assert late.status_code == 201 and late.json()["accepted"]
    assert early.status_code == 200 and not early.json()["accepted"]
    assert early.json()["check"]["note"] == "pozdě"
    assert "volunteer_email" not in early.json()["check"]
    assert resend.json()["accepted"]
    assert Check.objects.get().note == "pozdě"
    assert not Check.objects.get().is_confirmed


def test_resent_photo_replaces_the_one_with_its_order(
    anonymous, batch, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buffer, format="PNG")
    photo = f"data:image/png;filename=a.png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    check = anonymous.post(
        f"{API}/links/{batch.token}/checks/",
        link_check(batch.boxes.get()),
        format="json",
    ).json()["check"]
    url = f"{API}/links/{batch.token}/check_photos/"

    for order in (0, 0, 1):
        response = anonymous.post(
            url,
            {"parent_id": check["id"], "photo": photo, "order": order},
            format="json",
        )
        assert response.status_code == 201

    assert sorted(Check.objects.get().photos.values_list("order", flat=True)) == [0, 1]


def test_volunteer_hangs_a_new_box(anonymous, batch, types):
    box_id, check_id = uuid4(), uuid4()
    payload = {
        "id": str(box_id),
        "name": "1",
        "location": geojson(near(east=3)),
        "type_id": types["velky_sykornik"].pk,
        "hole_shape": "round",
        "hole_size": 33,
        "opening": "front",
        "installed_on": "2025-11-01",
        "check": {
            "id": str(check_id),
            "date": "2025-11-01",
            "made_at": made_at(10).isoformat(),
            "volunteer_nickname": "Sýkorka",
            "volunteer_email": "sykorka@example.com",
        },
    }
    response = anonymous.post(
        f"{API}/links/{batch.token}/boxes/", payload, format="json"
    )
    resend = anonymous.post(
        f"{API}/links/{batch.token}/boxes/", payload | {"name": "1b"}, format="json"
    )

    assert response.status_code == 201
    assert response.json()["warnings"]["duplicate_names"]
    assert response.json()["warnings"]["spacing"][0]["should_be_moved"]
    assert response.json()["check"]["box_changes"]["hung"]
    assert resend.status_code == 201
    box = NestBox.objects.get(pk=box_id)
    assert box.name == "1b" and box.status == NestBox.Status.PLANNED
    assert batch.boxes.filter(pk=box_id).exists()
    assert Check.objects.get().pk == check_id


def test_confirming_the_batch_applies_box_changes(
    anonymous, budkar_client, batch, types
):
    box = batch.boxes.get()
    changes = {
        "name": "1A",
        "location": geojson(near(north=10)),
        "hole_shape": "round",
        "hole_size": 28,
        "type": types["maly_sykornik"].pk,
        "opening": "roof",
    }
    anonymous.post(
        f"{API}/links/{batch.token}/checks/",
        link_check(box, box_changes=changes, box_left="needs_repair"),
        format="json",
    )

    response = budkar_client.post(f"{API}/batches/{batch.pk}/confirm/")

    assert response.status_code == 200
    assert response.json()["closed_at"]
    box = NestBox.objects.with_is_verified().get(pk=box.pk)
    assert (box.name, box.hole_size, box.opening) == ("1A", 28, "roof")
    assert box.status == NestBox.Status.NEEDS_REPAIR
    assert box.is_verified
    assert Check.objects.get().is_confirmed


def test_invalid_box_changes_are_rejected(anonymous, batch):
    response = anonymous.post(
        f"{API}/links/{batch.token}/checks/",
        link_check(batch.boxes.get(), box_changes={"colour": "red"}),
        format="json",
    )
    assert response.status_code == 400
    assert "box_changes" in response.json()


def test_a_check_answers_what_the_form_asks(anonymous, batch):
    url = f"{API}/links/{batch.token}/checks/"
    box = batch.boxes.get()

    response = anonymous.post(
        url, link_check(box, cleaning="not_cleaned"), format="json"
    )
    assert response.status_code == 400
    assert set(response.json()) == {"not_cleaned_reason"}

    lost = link_check(box, **NOT_FOUND | {"note": "", "contents": ["nothing"]})
    response = anonymous.post(url, lost, format="json")
    assert set(response.json()) == {"note", "contents"}


def test_managers_single_check_is_confirmed_at_once(budkar_client, make_box, manager):
    box = make_box()
    response = budkar_client.post(
        f"{API}/checks/",
        {
            "box_id": str(box.pk),
            "date": "2025-11-02",
            "found": "not_found",
            "contents": [],
            "note": "strom je pokácený",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["is_confirmed"]
    assert response.json()["entered_by"]["id"] == str(manager.pk)
    box.refresh_from_db()
    assert box.status == NestBox.Status.MISSING

    second = budkar_client.post(
        f"{API}/checks/",
        {"box_id": str(box.pk), "date": "2026-02-01", "found": "found", "contents": []},
        format="json",
    )
    assert second.status_code == 400

    fixed = budkar_client.patch(
        f"{API}/checks/{response.json()['id']}/",
        {
            "found": "found",
            "cleaning": "cleaned",
            "contents": ["nothing"],
            "box_left": "fine",
        },
        format="json",
    )
    assert fixed.status_code == 200
    box.refresh_from_db()
    assert box.status == NestBox.Status.IN_USE


def test_managers_check_into_a_batch_stays_pending(budkar_client, batch, make_box):
    box = make_box("2", location=near(east=100))
    response = budkar_client.post(
        f"{API}/checks/",
        {
            "box_id": str(box.pk),
            "batch_id": batch.pk,
            "date": "2025-11-02",
            "found": "found",
            "cleaning": "cleaned",
            "contents": ["bird_nest"],
            "box_left": "fine",
        },
        format="json",
    )
    assert response.status_code == 201
    assert not response.json()["is_confirmed"]
    assert batch.boxes.filter(pk=box.pk).exists()


def test_manager_deletes_a_check(budkar_client, batch, anonymous):
    anonymous.post(
        f"{API}/links/{batch.token}/checks/",
        link_check(batch.boxes.get()),
        format="json",
    )
    check = Check.objects.get()

    assert budkar_client.delete(f"{API}/checks/{check.pk}/").status_code == 204
    assert not Check.objects.exists()


def test_batch_defaults_to_the_suggested_boxes(budkar_client, area, make_box):
    box = make_box()
    make_box("2", location=near(east=100), status=NestBox.Status.PLANNED)

    response = budkar_client.post(
        f"{API}/batches/", {"area_id": area.pk, "name": "Jaro"}, format="json"
    )

    assert response.status_code == 201
    assert response.json()["box_ids"] == [str(box.pk)]
    assert response.json()["box_count"] == 1
    batch_id = response.json()["id"]
    removed = budkar_client.post(
        f"{API}/batches/{batch_id}/remove_boxes/",
        {"box_ids": [str(box.pk)]},
        format="json",
    )
    assert removed.json()["box_ids"] == []
    closed = budkar_client.post(f"{API}/batches/{batch_id}/close/")
    assert closed.json()["closed_at"]
    assert budkar_client.get(f"{API}/batches/open/").json() == []


def test_box_writes_return_warnings_and_history(budkar_client, area, make_box, types):
    make_box()
    response = budkar_client.post(
        f"{API}/boxes/",
        {
            "area_id": area.pk,
            "name": "1",
            "status": "in_use",
            "location": geojson(near(east=2)),
            "type_id": types["velky_sykornik"].pk,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["warnings"]["spacing"][0]["distance"] < 3
    assert response.json()["warnings"]["duplicate_names"]
    box_id = response.json()["id"]
    budkar_client.patch(f"{API}/boxes/{box_id}/", {"name": "2"}, format="json")
    history = budkar_client.get(f"{API}/boxes/{box_id}/history/").json()
    assert history[0]["changes"]["name"] == ["1", "2"]
    assert (
        budkar_client.patch(
            f"{API}/boxes/{box_id}/", {"status": "ended"}, format="json"
        ).status_code
        == 400
    )
    assert (
        budkar_client.patch(
            f"{API}/boxes/{box_id}/", {"status": "planned"}, format="json"
        ).status_code
        == 400
    )


def test_gpx_roundtrip(budkar_client, area, make_box):
    make_box("1")
    make_box("2", location=near(east=100))

    exported = budkar_client.get(f"{API}/areas/{area.pk}/export.gpx/")
    assert exported.status_code == 200
    gpx = exported.content.decode()
    assert "<name>2</name>" in gpx

    unchanged = budkar_client.post(
        f"{API}/areas/{area.pk}/import_gpx/", {"gpx": gpx}, format="json"
    ).json()
    assert {row["action"] for row in unchanged["rows"]} == {"unchanged"}

    edited = gpx.replace(
        "</gpx>", '<wpt lat="50.1" lon="14.5"><name>3</name></wpt></gpx>'
    )
    dry_run = budkar_client.post(
        f"{API}/areas/{area.pk}/import_gpx/", {"gpx": edited}, format="json"
    ).json()
    assert [row["action"] for row in dry_run["rows"]] == [
        "unchanged",
        "unchanged",
        "new",
    ]
    assert NestBox.objects.count() == 2

    applied = budkar_client.post(
        f"{API}/areas/{area.pk}/import_gpx/",
        {"gpx": edited, "apply": True, "installed_on": "2025-10-01"},
        format="json",
    ).json()
    assert applied["applied"]
    new = NestBox.objects.get(name="3")
    assert new.installed_on == date(2025, 10, 1)
    assert not NestBox.objects.with_is_verified().get(pk=new.pk).is_verified


def test_xlsx_export(budkar_client, area, make_box):
    make_box()
    response = budkar_client.get(f"{API}/areas/{area.pk}/export.xlsx/")
    assert response.status_code == 200
    assert b"".join(response.streaming_content)[:2] == b"PK"


def test_want_to_hang_sends_an_email(anonymous):
    with patch("nest_boxes.emails.text") as text:
        response = anonymous.post(
            f"{API}/public/want_to_hang/",
            {
                "name": "Jana <b>",
                "email": "jana@example.com",
                "place": "Brno",
                "box_source": "make",
                "message": "Ahoj",
            },
            format="json",
        )

    assert response.status_code == 204
    recipients, _subject, content = text.call_args.args
    assert "hnuti@brontosaurus.cz" in recipients
    assert "Jana &lt;b&gt;" in content and "Chceme je vyrobit" in content
    assert text.call_args.kwargs["reply_to"] == ["jana@example.com"]


def test_open_batches_reminder(batch, stranger):
    from nest_boxes.emails import open_batches_reminder

    Batch.objects.filter(pk=batch.pk).update(created_at=now().replace(year=2024))
    with patch("nest_boxes.emails.text") as text:
        open_batches_reminder()
    # Nobody opened the seeded batch
    text.assert_not_called()

    Batch.objects.filter(pk=batch.pk).update(created_by=stranger)
    with patch("nest_boxes.emails.text") as text:
        open_batches_reminder()
    assert text.call_args.args[0] == [stranger.email]
    assert batch.name in text.call_args.args[2]


def test_help_articles_are_written_by_budkar_only(client_for, stranger, budkar_client):
    url = f"{API}/help_articles/found/"
    payload = {"title": "Nalezena", "content": "<p>Ano<script>x</script></p>"}

    assert client_for(stranger).patch(url, payload, format="json").status_code == 403
    response = budkar_client.patch(url, payload, format="json")
    assert response.json()["content"] == "<p>Ano</p>"
    assert budkar_client.get(f"{API}/help_articles/nope/").status_code == 404


@override_settings(TESTING=True)
def test_e2e_seed(anonymous, movement):
    first = anonymous.post(f"{API}/testing/seed/").json()
    second = anonymous.post(f"{API}/testing/seed/").json()

    assert first.pop("open_batch_id") != second.pop("open_batch_id")
    assert first == second
    assert anonymous.get(f"{API}/links/{first['open_token']}/").status_code == 200
    assert anonymous.get(f"{API}/links/{first['closed_token']}/").status_code == 410


@override_settings(TESTING=False)
def test_seed_is_off_outside_tests(anonymous):
    assert anonymous.post(f"{API}/testing/seed/").status_code == 404


@pytest.fixture
def season_2025(monkeypatch):
    monkeypatch.setattr(Check, "current_season", staticmethod(lambda: 2025))


def test_season_states_per_area(budkar_client, area, other_unit, make_box, types):
    make_box("1")
    make_box("2", location=near(east=100), status=NestBox.Status.NEEDS_REPAIR)
    make_box("3", location=near(east=200), type=types["netopyrnik"])
    make_box("4", location=near(east=300), verified=True)
    url = f"{API}/areas/season_states/"

    counts = {"area_id": area.pk, "planned": 0, "to_check": 2, "attention": 1}
    assert budkar_client.get(url).json() == [counts | {"done": 1}]
    assert budkar_client.get(
        url, {"type": types["velky_sykornik"].pk, "is_verified": False}
    ).json() == [counts | {"to_check": 1, "done": 0}]
    assert budkar_client.get(url, {"season_state": "attention"}).json() == [
        counts | {"to_check": 0, "done": 0}
    ]
    assert budkar_client.get(url, {"administration_unit": other_unit.pk}).json() == []
    assert budkar_client.get(url, {"season_state": "nonsense"}).status_code == 400
    only_4 = [counts | {"to_check": 1, "attention": 0, "done": 0}]
    assert (
        budkar_client.get(url, {"last_checked_before": "2026-07-01"}).json() == only_4
    )
    assert budkar_client.get(url, {"last_checked_after": "2020-01-01"}).json() == only_4
    assert budkar_client.get(url, {"last_checked_after": "2021-01-01"}).json() == []
    assert budkar_client.get(url, {"never_checked": True}).json() == [
        counts | {"to_check": 1, "done": 1}
    ]


def test_boxes_by_problem(budkar_client, make_box):
    make_box("1")
    make_box("R", location=near(east=100), status=NestBox.Status.NEEDS_REPAIR)
    make_box("M", location=near(east=200), status=NestBox.Status.MISSING)

    def names(*problems):
        boxes = budkar_client.get(f"{API}/boxes/", {"problem": problems}).json()
        return sorted(box["name"] for box in boxes["results"])

    assert names("needs_repair") == ["R"]
    assert names("needs_repair", "missing") == ["M", "R"]
    assert names("moved") == []
    assert names("not_cleaned") == []
    counts = budkar_client.get(
        f"{API}/areas/season_states/", {"problem": "missing"}
    ).json()
    assert [(row["attention"], row["to_check"]) for row in counts] == [(1, 0)]


def test_problems_follow_this_seasons_pending_check(
    budkar_client, make_box, season_2025
):
    """As the map's state does: a pending check counts as if it were confirmed."""
    gone = make_box("G")
    repaired = make_box(
        "R", location=near(east=100), status=NestBox.Status.NEEDS_REPAIR
    )
    dirty = make_box("D", location=near(east=200))
    found = dict(date=date(2025, 11, 1), made_at=made_at(10), found=Check.Found.FOUND)
    Check.objects.create(box=gone, **found | {"found": Check.Found.NOT_FOUND})
    Check.objects.create(box=repaired, box_left=Check.BoxLeft.FINE, **found)
    Check.objects.create(
        box=dirty,
        box_left=Check.BoxLeft.FINE,
        cleaning=Check.Cleaning.NOT_CLEANED,
        **found,
    )

    def names(*problems):
        boxes = budkar_client.get(f"{API}/boxes/", {"problem": problems}).json()
        return sorted(box["name"] for box in boxes["results"])

    assert names("missing") == ["G"]
    assert names("needs_repair") == []
    assert names("not_cleaned") == ["D"]


def test_boxes_by_legend_entry(budkar_client, make_box):
    make_box("1")
    make_box("E", location=near(east=100), status=NestBox.Status.ENDED)
    make_box("P", location=near(east=200), status=NestBox.Status.PLANNED)

    def names(*states):
        boxes = budkar_client.get(f"{API}/boxes/", {"state": states}).json()
        return sorted(box["name"] for box in boxes["results"])

    assert names("to_check", "ended") == ["1", "E"]
    assert names("planned") == ["P"]


def test_boxes_in_a_bounding_box(budkar_client, make_box):
    make_box("1")
    make_box("2", location=near(east=5000))
    west, south = near(east=-100, north=-100).coords
    east, north = near(east=100, north=100).coords

    boxes = budkar_client.get(
        f"{API}/boxes/", {"bbox": f"{west},{south},{east},{north}"}
    ).json()["results"]

    assert [(box["name"], box["season_state"]) for box in boxes] == [("1", "to_check")]
    assert budkar_client.get(f"{API}/boxes/", {"bbox": "1,2"}).status_code == 400


def test_volunteer_gets_the_season_state(anonymous, batch, season_2025):
    url = f"{API}/links/{batch.token}/"
    assert anonymous.get(url).json()["boxes"][0]["season_state"] == "to_check"

    sent = anonymous.post(
        f"{url}checks/", link_check(batch.boxes.get(), **NOT_FOUND), format="json"
    )

    assert sent.json()["season_state"] == "attention"
    assert anonymous.get(url).json()["boxes"][0]["season_state"] == "attention"


def test_a_signed_in_link_check_names_its_author(
    anonymous, budkar_client, budkar, batch, season_2025
):
    url = f"{API}/links/{batch.token}/checks/"
    box = batch.boxes.get()
    anonymous.post(url, link_check(box, **NOT_FOUND), format="json")
    assert Check.objects.get().entered_by is None

    budkar_client.post(url, link_check(box, hour=11, **NOT_FOUND), format="json")
    assert Check.objects.get().entered_by == budkar


def test_map_of_boxes_has_constant_queries(
    budkar_client, make_box, django_assert_num_queries
):
    make_box("1")
    url = f"{API}/boxes/map/"
    # The first request caches the movement and the roles
    budkar_client.get(url)
    with CaptureQueriesContext(connection) as one_box:
        budkar_client.get(url)
    make_box("2", location=near(east=100))
    make_box("3", location=near(east=200))

    with django_assert_num_queries(len(one_box)):
        boxes = budkar_client.get(url).json()

    assert sorted(box["name"] for box in boxes) == ["1", "2", "3"]
    assert set(boxes[0]) == {
        "id",
        "name",
        "previous_names",
        "area_id",
        "location",
        "planned_radius",
        "type_id",
        "status",
        "is_verified",
        "is_new",
        "should_be_moved",
        "season_state",
        "season_status",
        "season_cleaning",
        "last_checked_on",
    }
    assert boxes[0]["season_state"] == "to_check"


def test_public_regions_never_show_box_coordinates(anonymous, region, make_box):
    box = make_box(location=near(east=123, north=45))
    make_box("2", location=near(east=-200, north=-80), status=NestBox.Status.ENDED)
    make_box("abroad", location=near(east=200_000))

    regions = anonymous.get(f"{API}/public/regions/").json()

    assert [(r["name"], r["box_count"]) for r in regions] == [
        ("Praha", 1),
        ("V zahraničí", 1),
    ]
    assert regions[0]["marker"]["type"] == "Point"
    assert not contains_coordinates(regions, box.location)


def test_public_figures_are_cached_until_a_box_changes(
    anonymous, region, make_box, django_capture_on_commit_callbacks
):
    def box_counts():
        regions = anonymous.get(f"{API}/public/regions/").json()
        return [region["box_count"] for region in regions]

    with django_capture_on_commit_callbacks(execute=True):
        box = make_box(location=near(east=123, north=45))
    assert box_counts() == [1, 0]

    with CaptureQueriesContext(connection) as queries:
        assert box_counts() == [1, 0]
    assert not queries

    with django_capture_on_commit_callbacks(execute=True):
        box.status = NestBox.Status.ENDED
        box.save()
    assert box_counts() == [0, 0]


def test_only_a_planned_box_is_deleted(budkar_client, make_box):
    hanging = make_box("1")
    planned = make_box("P", location=near(east=100), status=NestBox.Status.PLANNED)

    assert budkar_client.delete(f"{API}/boxes/{hanging.pk}/").status_code == 400
    assert budkar_client.delete(f"{API}/boxes/{planned.pk}/").status_code == 204
    assert list(NestBox.objects.all()) == [hanging]
