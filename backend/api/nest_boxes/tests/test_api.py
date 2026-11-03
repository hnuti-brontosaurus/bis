import base64
import io
import json
from datetime import date
from unittest.mock import patch
from uuid import uuid4

import pytest
from administration_units.models import AdministrationUnit
from api.nest_boxes.tests.conftest import API
from bis.helpers import paused_validation
from django.test import override_settings
from django.utils.timezone import now
from nest_boxes.checks import close_batch
from nest_boxes.models import Area, Batch, Check, HelpArticle, NestBox
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
        "volunteer_nickname": "Sýkorka",
        "volunteer_email": "sykorka@example.com",
    } | kwargs


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
    ["areas/", "boxes/", "checks/", "batches/", "batches/open/"],
)
def test_non_managers_are_refused(anonymous, client_for, stranger, area, url):
    assert anonymous.get(f"{API}/{url}").status_code == 403
    assert client_for(stranger).get(f"{API}/{url}").status_code == 403


def test_board_member_sees_only_the_units_areas(board_client, area, unit, make_box):
    make_box()
    with paused_validation():
        other_unit = AdministrationUnit.objects.create(
            name="Jiný", abbreviation="J", is_for_kids=False, category=unit.category
        )
    other_unit_area = Area.objects.create(name="Cizí", administration_unit=other_unit)
    NestBox.objects.create(
        area=other_unit_area, name="X", location=near(), status=NestBox.Status.IN_USE
    )

    areas = board_client.get(f"{API}/areas/").json()["results"]
    boxes = board_client.get(f"{API}/boxes/").json()["results"]

    assert [a["id"] for a in areas] == [area.pk]
    assert {b["area_id"] for b in boxes} == {area.pk}
    assert (
        board_client.post(
            f"{API}/areas/", {"name": "Nová", "administration_unit_id": unit.pk}
        ).status_code
        == 403
    )


def test_budkar_creates_areas(client_for, budkar, unit):
    response = client_for(budkar).post(
        f"{API}/areas/", {"name": "Nová", "administration_unit_id": unit.pk}
    )
    assert response.status_code == 201


def test_whoami(anonymous, board_client, area, batch):
    assert anonymous.get(f"{API}/whoami/").json()["user"] is None
    data = board_client.get(f"{API}/whoami/").json()
    assert data["managed_area_ids"] == [area.pk]
    assert data["open_batch_count"] == 1
    assert not data["is_budkar"]


def test_volunteer_sees_only_the_batchs_boxes(anonymous, batch, make_box):
    outside = make_box("2", location=near(east=300, north=200))

    data = anonymous.get(f"{API}/links/{batch.token}/").json()

    assert [box["id"] for box in data["boxes"]] == [str(batch.boxes.get().pk)]
    assert not contains_coordinates(data, outside.location)
    assert "owner_note" not in data["boxes"][0]
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


def test_volunteer_adds_a_pending_box(anonymous, batch, types):
    box_id = uuid4()
    payload = {
        "id": str(box_id),
        "name": "1",
        "location": geojson(near(east=3)),
        "type_id": types["velky_sykornik"].pk,
        "hole_shape": "round",
        "hole_size": 33,
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
    assert resend.status_code == 201
    box = NestBox.objects.get(pk=box_id)
    assert box.name == "1b" and not box.is_confirmed
    assert batch.boxes.filter(pk=box_id).exists()


def test_confirming_the_batch_applies_box_changes(
    anonymous, board_client, batch, types
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

    response = board_client.post(f"{API}/batches/{batch.pk}/confirm/")

    assert response.status_code == 200
    assert response.json()["closed_at"]
    box.refresh_from_db()
    assert (box.name, box.hole_size, box.opening) == ("1A", 28, "roof")
    assert box.condition == NestBox.Condition.NEEDS_REPAIR
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


def test_managers_single_check_is_confirmed_at_once(board_client, make_box, manager):
    box = make_box()
    response = board_client.post(
        f"{API}/checks/",
        {
            "box_id": str(box.pk),
            "date": "2025-11-02",
            "found": "not_found",
            "contents": [],
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["is_confirmed"]
    assert response.json()["entered_by"]["id"] == str(manager.pk)
    box.refresh_from_db()
    assert box.status == NestBox.Status.MISSING

    second = board_client.post(
        f"{API}/checks/",
        {"box_id": str(box.pk), "date": "2026-02-01", "found": "found", "contents": []},
        format="json",
    )
    assert second.status_code == 400

    fixed = board_client.patch(
        f"{API}/checks/{response.json()['id']}/",
        {"found": "found", "contents": ["nothing"]},
        format="json",
    )
    assert fixed.status_code == 200
    box.refresh_from_db()
    assert box.status == NestBox.Status.IN_USE


def test_managers_check_into_a_batch_stays_pending(board_client, batch, make_box):
    box = make_box("2", location=near(east=100))
    response = board_client.post(
        f"{API}/checks/",
        {
            "box_id": str(box.pk),
            "batch_id": batch.pk,
            "date": "2025-11-02",
            "found": "found",
            "contents": ["bird_nest"],
        },
        format="json",
    )
    assert response.status_code == 201
    assert not response.json()["is_confirmed"]
    assert batch.boxes.filter(pk=box.pk).exists()


def test_manager_deletes_a_check(board_client, batch, anonymous):
    anonymous.post(
        f"{API}/links/{batch.token}/checks/",
        link_check(batch.boxes.get()),
        format="json",
    )
    check = Check.objects.get()

    assert board_client.delete(f"{API}/checks/{check.pk}/").status_code == 204
    assert not Check.objects.exists()


def test_batch_defaults_to_the_suggested_boxes(board_client, area, make_box):
    box = make_box()
    make_box("2", location=near(east=100), status=NestBox.Status.PLANNED)

    response = board_client.post(
        f"{API}/batches/", {"area_id": area.pk, "name": "Jaro"}, format="json"
    )

    assert response.status_code == 201
    assert response.json()["box_ids"] == [str(box.pk)]
    assert response.json()["box_count"] == 1
    batch_id = response.json()["id"]
    removed = board_client.post(
        f"{API}/batches/{batch_id}/remove_boxes/",
        {"box_ids": [str(box.pk)]},
        format="json",
    )
    assert removed.json()["box_ids"] == []
    closed = board_client.post(f"{API}/batches/{batch_id}/close/")
    assert closed.json()["closed_at"]
    assert board_client.get(f"{API}/batches/open/").json() == []


def test_box_writes_return_warnings_and_history(board_client, area, make_box, types):
    make_box()
    response = board_client.post(
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
    board_client.patch(f"{API}/boxes/{box_id}/", {"name": "2"}, format="json")
    history = board_client.get(f"{API}/boxes/{box_id}/history/").json()
    assert history[0]["changes"]["name"] == ["1", "2"]
    assert (
        board_client.patch(
            f"{API}/boxes/{box_id}/", {"status": "ended"}, format="json"
        ).status_code
        == 400
    )


def test_gpx_roundtrip(board_client, area, make_box):
    make_box("1")
    make_box("2", location=near(east=100))

    exported = board_client.get(f"{API}/areas/{area.pk}/export.gpx/")
    assert exported.status_code == 200
    gpx = exported.content.decode()
    assert "<name>2</name>" in gpx

    unchanged = board_client.post(
        f"{API}/areas/{area.pk}/import_gpx/", {"gpx": gpx}, format="json"
    ).json()
    assert {row["action"] for row in unchanged["rows"]} == {"unchanged"}

    edited = gpx.replace(
        "</gpx>", '<wpt lat="50.1" lon="14.5"><name>3</name></wpt></gpx>'
    )
    dry_run = board_client.post(
        f"{API}/areas/{area.pk}/import_gpx/", {"gpx": edited}, format="json"
    ).json()
    assert [row["action"] for row in dry_run["rows"]] == [
        "unchanged",
        "unchanged",
        "new",
    ]
    assert NestBox.objects.count() == 2

    applied = board_client.post(
        f"{API}/areas/{area.pk}/import_gpx/",
        {"gpx": edited, "apply": True, "installed_on": "2025-10-01"},
        format="json",
    ).json()
    assert applied["applied"]
    new = NestBox.objects.get(name="3")
    assert new.installed_on == date(2025, 10, 1)
    assert new.is_confirmed and not new.is_verified


def test_xlsx_export(board_client, area, make_box):
    make_box()
    response = board_client.get(f"{API}/areas/{area.pk}/export.xlsx/")
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


def test_open_batches_reminder(batch, board_member):
    from nest_boxes.emails import open_batches_reminder

    Batch.objects.filter(pk=batch.pk).update(created_at=now().replace(year=2024))
    with patch("nest_boxes.emails.text") as text:
        open_batches_reminder()

    assert text.call_args.args[0] == [board_member.email]
    assert batch.name in text.call_args.args[2]


def test_help_articles_are_written_by_budkar_only(client_for, budkar, board_client):
    url = f"{API}/help_articles/found/"
    payload = {"title": "Nalezena", "content": "<p>Ano<script>x</script></p>"}

    assert board_client.patch(url, payload, format="json").status_code == 403
    response = client_for(budkar).patch(url, payload, format="json")
    assert response.json()["content"] == "<p>Ano</p>"
    assert board_client.get(f"{API}/help_articles/nope/").status_code == 404


@override_settings(TESTING=True)
def test_e2e_seed(anonymous, movement):
    first = anonymous.post(f"{API}/testing/seed/").json()
    second = anonymous.post(f"{API}/testing/seed/").json()

    assert first.pop("open_batch_id") != second.pop("open_batch_id")
    assert first == second
    assert anonymous.get(f"{API}/links/{first['open_token']}/").status_code == 200
    assert anonymous.get(f"{API}/links/{first['closed_token']}/").status_code == 410


def test_seed_is_off_outside_tests(anonymous):
    assert anonymous.post(f"{API}/testing/seed/").status_code == 404
