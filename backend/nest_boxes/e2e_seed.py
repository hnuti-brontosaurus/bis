"""The fixture set the nest box SPA's Playwright specs run against, see CLAUDE.md.

Rerunning it resets the seeded area to the same boxes, batches and ids.
"""

from datetime import date
from uuid import UUID

from administration_units.models import AdministrationUnit, BrontosaurusMovement
from bis.helpers import paused_validation
from bis.models import User
from categories.models import AdministrationUnitCategory, NestBoxType
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.core.management import call_command
from nest_boxes.models import Area, Batch, NestBox

PASSWORD = "nest-boxes-e2e"
BUDKAR_EMAIL = "budkar@budky.nope"
MEMBER_EMAIL = "clen@budky.nope"
AREA_NAME = "E2E Cibulka"
OPEN_TOKEN = UUID("00000000-0000-4000-8000-000000000001")
CLOSED_TOKEN = UUID("00000000-0000-4000-8000-000000000002")
BOX_IDS = {
    "1": UUID("00000000-0000-4000-8000-000000000011"),
    "2": UUID("00000000-0000-4000-8000-000000000012"),
    "3": UUID("00000000-0000-4000-8000-000000000013"),
    "P1": UUID("00000000-0000-4000-8000-000000000014"),
}


def _user(email, first_name):
    user, _ = User.objects.get_or_create(
        email=email, defaults={"first_name": first_name, "last_name": "E2E"}
    )
    user.set_password(PASSWORD)
    user.save()
    return user


def seed():
    call_command("create_categories", group="bis")
    call_command("create_categories", group="nest_boxes")
    budkar = _user(BUDKAR_EMAIL, "Budkař")
    _user(MEMBER_EMAIL, "Člen")

    movement = BrontosaurusMovement.objects.first()
    if movement is None:
        director = _user("reditel@budky.nope", "Ředitel")
        movement = BrontosaurusMovement.objects.create(
            director=director, finance_director=director
        )
    movement.nest_box_managers.add(budkar)
    cache.delete("brontosaurus_movement")
    budkar.update_roles()

    with paused_validation():
        unit, _ = AdministrationUnit.objects.get_or_create(
            abbreviation="Budky E2E",
            defaults=dict(
                name="ZČ Budky E2E",
                is_for_kids=False,
                phone="+420123456789",
                email="budky-e2e@budky.nope",
                category=AdministrationUnitCategory.objects.get(slug="basic_section"),
            ),
        )
    area, _ = Area.objects.get_or_create(
        name=AREA_NAME, defaults={"administration_unit": unit}
    )
    Batch.objects.filter(area=area).delete()
    NestBox.objects.filter(area=area).delete()

    box_type = NestBoxType.objects.get(slug="velky_sykornik")
    common = dict(
        area=area,
        type=box_type,
        hole_shape=NestBoxType.HoleShape.ROUND,
        hole_size=33,
        opening=NestBox.Opening.FRONT,
        installed_on=date(2020, 3, 1),
        status=NestBox.Status.IN_USE,
    )
    boxes = {
        "1": NestBox(location=Point(14.3600, 50.0700, srid=4326), **common),
        "2": NestBox(location=Point(14.3610, 50.0705, srid=4326), **common),
        # Imported and never verified, and left out of the open batch
        "3": NestBox(location=Point(14.3620, 50.0710, srid=4326), **common),
        "P1": NestBox(
            location=Point(14.3630, 50.0700, srid=4326),
            planned_radius=20,
            **common | {"status": NestBox.Status.PLANNED, "installed_on": None},
        ),
    }
    for name, box in boxes.items():
        box.id = BOX_IDS[name]
        box.name = name
        box.is_verified = name != "3"
    NestBox.objects.bulk_create(boxes.values())
    NestBox.recompute_distances(area.pk)

    open_batch = Batch.objects.create(
        area=area, name="Podzim E2E", token=OPEN_TOKEN, created_by=budkar
    )
    open_batch.boxes.set([boxes["1"], boxes["2"], boxes["P1"]])
    closed_batch = Batch.objects.create(
        area=area, name="Uzavřená E2E", token=CLOSED_TOKEN, created_by=budkar
    )
    closed_batch.boxes.set([boxes["1"]])
    closed_batch.closed_at = closed_batch.created_at
    closed_batch.save()

    return {
        "password": PASSWORD,
        "budkar_email": BUDKAR_EMAIL,
        "member_email": MEMBER_EMAIL,
        "area_id": area.pk,
        "open_batch_id": open_batch.pk,
        "open_token": str(OPEN_TOKEN),
        "closed_token": str(CLOSED_TOKEN),
        "box_ids": {name: str(pk) for name, pk in BOX_IDS.items()},
    }
