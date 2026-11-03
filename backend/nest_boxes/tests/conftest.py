from datetime import UTC, date, datetime
from math import cos, radians

import pytest
from administration_units.models import AdministrationUnit, BrontosaurusMovement
from bis.helpers import paused_validation
from bis.models import User
from categories.models import AdministrationUnitCategory, NestBoxType, RoleCategory
from django.contrib.gis.geos import Point, Polygon
from django.core.cache import cache
from django.core.management import call_command
from nest_boxes.models import Area, Batch, NestBox
from regions.models import Region

ORIGIN = Point(14.42, 50.08, srid=4326)
METRES_PER_DEGREE = 111_320


def near(east=0, north=0, origin=ORIGIN):
    """A point the given number of metres east and north of `origin`."""
    return Point(
        origin.x + east / (METRES_PER_DEGREE * cos(radians(origin.y))),
        origin.y + north / METRES_PER_DEGREE,
        srid=4326,
    )


def made_at(hour):
    return datetime(2025, 11, 1, hour, tzinfo=UTC)


@pytest.fixture(autouse=True)
def categories(db):
    call_command("create_categories", group="nest_boxes")


@pytest.fixture
def types():
    return {box_type.slug: box_type for box_type in NestBoxType.objects.all()}


@pytest.fixture
def movement(db):
    # BrontosaurusMovement.get() caches the singleton outside the test
    # transaction, and User.update_roles() needs it and the role rows
    cache.delete("brontosaurus_movement")
    for slug in ("director", "nest_box_manager", "board_member", "organizer"):
        RoleCategory.objects.get_or_create(slug=slug, defaults={"name": slug})
    director = User.objects.create(email="director@example.com")
    yield BrontosaurusMovement.objects.create(
        director=director, finance_director=director
    )
    cache.delete("brontosaurus_movement")


@pytest.fixture
def unit(db):
    with paused_validation():
        return AdministrationUnit.objects.create(
            name="ZČ Budky",
            abbreviation="Budky",
            is_for_kids=False,
            phone="+420123456789",
            email="budky@example.com",
            category=AdministrationUnitCategory.objects.create(
                name="Základní článek", slug="basic_section"
            ),
        )


@pytest.fixture
def region(db):
    return Region.objects.create(
        name="Praha",
        area=Polygon.from_bbox((14.2, 49.9, 14.7, 50.2)),
    )


@pytest.fixture
def area(unit):
    return Area.objects.create(name="Cibulka", administration_unit=unit)


@pytest.fixture
def make_box(area, types):
    def make(name="1", location=ORIGIN, **kwargs):
        defaults = dict(
            area=area,
            name=name,
            location=location,
            status=NestBox.Status.IN_USE,
            type=types["velky_sykornik"],
            hole_shape=NestBoxType.HoleShape.ROUND,
            hole_size=33,
            opening=NestBox.Opening.FRONT,
            installed_on=date(2020, 3, 1),
        )
        return NestBox.objects.create(**(defaults | kwargs))

    return make


@pytest.fixture
def batch(area, make_box):
    batch = Batch.objects.create(area=area, name="Podzim 2025")
    batch.boxes.add(make_box())
    return batch


@pytest.fixture
def manager(db):
    return User.objects.create(email="manager@example.com")
