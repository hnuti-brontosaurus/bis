"""GPX export and the two-step import: a dry run returns the rows, then they are applied."""

from dataclasses import dataclass, field
from math import asin, cos, radians, sin, sqrt
from xml.etree import ElementTree

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import transaction
from nest_boxes.boxes import create_box, spacing_warnings, update_box
from nest_boxes.models import PLACING_ANY_TYPE_LIMIT, PLACING_SAME_TYPE_LIMIT, NestBox

NAMESPACE = "http://www.topografix.com/GPX/1/1"
# A roundtrip through a GPS device rounds the coordinates; closer is the same spot
MOVE_THRESHOLD = 1
EARTH_RADIUS = 6_371_000


def metres_between(a, b):
    """Haversine: the file's waypoints are compared before any of them is stored."""
    lng1, lat1, lng2, lat2 = map(radians, (a.x, a.y, b.x, b.y))
    h = (
        sin((lat2 - lat1) / 2) ** 2
        + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    )
    return 2 * EARTH_RADIUS * asin(sqrt(h))


def export_gpx(boxes):
    ElementTree.register_namespace("", NAMESPACE)
    # Garmin devices refuse files from creators they don't know
    root = ElementTree.Element(
        f"{{{NAMESPACE}}}gpx", version="1.1", creator="Oregon 550"
    )
    for box in boxes:
        waypoint = ElementTree.SubElement(
            root,
            f"{{{NAMESPACE}}}wpt",
            lat=f"{box.location.y:.7f}",
            lon=f"{box.location.x:.7f}",
        )
        if box.elevation is not None:
            ElementTree.SubElement(waypoint, f"{{{NAMESPACE}}}ele").text = str(
                box.elevation
            )
        ElementTree.SubElement(waypoint, f"{{{NAMESPACE}}}name").text = box.name
        if box.type:
            ElementTree.SubElement(
                waypoint, f"{{{NAMESPACE}}}desc"
            ).text = box.type.name
    return ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)


def _local_name(element):
    return element.tag.rsplit("}", 1)[-1]


def parse_gpx(content):
    """[(name, Point)] of the file's waypoints, in GPX 1.0 or 1.1."""
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as error:
        raise ValidationError({"gpx": f"Soubor není platné GPX: {error}"})
    waypoints = []
    for number, waypoint in enumerate(
        (element for element in root.iter() if _local_name(element) == "wpt"), 1
    ):
        name = next(
            (
                (child.text or "").strip()
                for child in waypoint
                if _local_name(child) == "name"
            ),
            "",
        )
        if not name:
            raise ValidationError({"gpx": f"Bod č. {number} nemá označení."})
        try:
            point = Point(
                float(waypoint.get("lon")), float(waypoint.get("lat")), srid=4326
            )
        except (TypeError, ValueError):
            raise ValidationError({"gpx": f"Bod {name} nemá platné souřadnice."})
        waypoints.append((name, point))
    if not waypoints:
        raise ValidationError({"gpx": "Soubor neobsahuje žádné body."})
    return waypoints


@dataclass
class ImportRow:
    class Action:
        NEW = "new"
        MOVE = "move"
        UNCHANGED = "unchanged"
        # Several boxes in the area have the name; left for the manager to sort out
        AMBIGUOUS = "ambiguous"

    name: str
    location: Point
    action: str
    box: NestBox | None = None
    moved_by: float | None = None
    warnings: list = field(default_factory=list)
    # Other rows of the file closer than the placing limits
    close_rows: list = field(default_factory=list)


def import_rows(area, waypoints, box_type):
    """What importing the waypoints into the area would do, without doing it."""
    boxes = NestBox.objects.filter(area=area).exclude(status=NestBox.Status.ENDED)
    by_name = {}
    for box in boxes.select_related("type"):
        by_name.setdefault(box.name.strip().lower(), []).append(box)

    rows = []
    for name, location in waypoints:
        matches = by_name.get(name.lower(), [])
        if len(matches) > 1:
            rows.append(ImportRow(name, location, ImportRow.Action.AMBIGUOUS))
            continue
        if not matches:
            row = ImportRow(name, location, ImportRow.Action.NEW)
            row.warnings = spacing_warnings(area, location, box_type)
        else:
            box = matches[0]
            moved_by = metres_between(box.location, location)
            row = ImportRow(
                name,
                location,
                ImportRow.Action.MOVE
                if moved_by > MOVE_THRESHOLD
                else ImportRow.Action.UNCHANGED,
                box=box,
                moved_by=moved_by,
            )
            if row.action == ImportRow.Action.MOVE:
                row.warnings = spacing_warnings(area, location, box.type, box.pk)
        rows.append(row)

    placed = [
        (index, row)
        for index, row in enumerate(rows)
        if row.action in (ImportRow.Action.NEW, ImportRow.Action.MOVE)
    ]
    for index, row in placed:
        row_type = row.box.type if row.box else box_type
        for other_index, other in placed:
            if other_index == index:
                continue
            other_type = other.box.type if other.box else box_type
            same_type = row_type is not None and row_type == other_type
            limit = PLACING_SAME_TYPE_LIMIT if same_type else PLACING_ANY_TYPE_LIMIT
            if metres_between(row.location, other.location) < limit:
                row.close_rows.append(other_index)
    return rows


@transaction.atomic
def apply_import(area, rows, skip, user, date, installed_on, box_type):
    """Creates the new boxes and moves the moved ones, leaving out the rows in `skip`."""
    for index, row in enumerate(rows):
        if index in skip:
            continue
        if row.action == ImportRow.Action.NEW:
            row.box = create_box(
                {
                    "area": area,
                    "name": row.name,
                    "location": row.location,
                    "status": NestBox.Status.IN_USE,
                    "installed_on": installed_on,
                    "type": box_type,
                    "hole_shape": box_type.hole_shape if box_type else "",
                },
                user,
                date,
            )
        elif row.action == ImportRow.Action.MOVE:
            update_box(row.box, {"location": row.location}, user, date)
