from dataclasses import dataclass

from categories.models import NestBoxType
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.exceptions import ValidationError
from django.db import models as m
from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Q
from nest_boxes.models import (
    EXISTING_ANY_TYPE_LIMIT,
    EXISTING_SAME_TYPE_LIMIT,
    PLACING_ANY_TYPE_LIMIT,
    PLACING_SAME_TYPE_LIMIT,
    Batch,
    Check,
    NestBox,
    NestBoxHistory,
    SeasonState,
)

NEW_BOX_REQUIRED_FIELDS = (
    "name",
    "location",
    "hole_shape",
    "type",
    "opening",
    "installed_on",
)
MEASURED_HOLE_SHAPES = (NestBoxType.HoleShape.ROUND, NestBoxType.HoleShape.OVAL)


def suggest_type(hole_shape, hole_size):
    if not hole_shape:
        return None
    types = NestBoxType.objects.filter(hole_shape=hole_shape)
    if hole_size is None:
        types = types.filter(hole_min=None, hole_max=None)
    else:
        types = types.filter(
            Q(hole_min=None) | Q(hole_min__lte=hole_size),
            Q(hole_max=None) | Q(hole_max__gte=hole_size),
        )
    return types.first()


def _to_json(value):
    if isinstance(value, Point):
        return list(value.coords)
    if isinstance(value, m.Model):
        return value.pk
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


@transaction.atomic
def update_box(box, values, user, date, box_check=None):
    """The one way to change a box: saves it and records the change in its history."""
    if (
        "location" in values
        and values["location"] != box.location
        and "elevation" not in values
    ):
        # The old elevation belongs to the old spot; fill_nest_box_elevations refills it
        values = {**values, "elevation": None}
    changes = {}
    for field, value in values.items():
        old = getattr(box, field)
        if old != value:
            changes[field] = [_to_json(old), _to_json(value)]
            setattr(box, field, value)
    if changes:
        box.save()
        NestBoxHistory.objects.create(
            box=box, date=date, user=user, box_check=box_check, changes=changes
        )
    if "area" in changes:
        # A batch holds the boxes of its own area only
        for batch in box.batches.filter(closed_at=None).exclude(area=box.area):
            batch.boxes.remove(box)
    return changes


@transaction.atomic
def create_box(values, user, date):
    """A new box, with its starting values as the first history entry."""
    box = NestBox(**values, created_by=user)
    box.save()
    record_start(box, values, user, date)
    return box


def record_start(box, values, user, date, box_check=None):
    NestBoxHistory.objects.create(
        box=box,
        date=date,
        user=user,
        box_check=box_check,
        changes={
            field: [None, _to_json(value)]
            for field, value in values.items()
            if field != "id"
        },
    )


def missing_for_new_box(box):
    missing = [field for field in NEW_BOX_REQUIRED_FIELDS if not getattr(box, field)]
    if box.hole_shape in MEASURED_HOLE_SHAPES and box.hole_size is None:
        missing.append("hole_size")
    return missing


def end_box(box, end_reason, ended_on, user):
    update_box(
        box,
        {
            "status": NestBox.Status.ENDED,
            "end_reason": end_reason,
            "ended_on": ended_on,
        },
        user,
        ended_on,
    )


def delete_box(box):
    """A plan that was never hung leaves no trace; a box that hung is ended instead."""
    if box.status != NestBox.Status.PLANNED:
        raise ValidationError("Smazat lze jen plánovanou budku.")
    box.delete()


@dataclass
class SpacingWarning:
    box: NestBox
    distance: float
    is_same_type: bool
    # Inside the limits for existing boxes: the new box would show "should be
    # moved" straight away, so the question needs a stronger wording
    should_be_moved: bool


def spacing_warnings(area, location, box_type, exclude_id=None):
    """Boxes in use in the area too close to a box being placed or moved there."""
    nearby = (
        NestBox.objects.in_use()
        .filter(
            area=area, location__distance_lt=(location, D(m=PLACING_SAME_TYPE_LIMIT))
        )
        .exclude(pk=exclude_id)
        .annotate(distance=Distance("location", location))
        .order_by("distance")
    )
    warnings = []
    for box in nearby:
        distance = box.distance.m
        is_same_type = box_type is not None and box.type_id == box_type.pk
        if is_same_type or distance < PLACING_ANY_TYPE_LIMIT:
            warnings.append(
                SpacingWarning(
                    box=box,
                    distance=distance,
                    is_same_type=is_same_type,
                    should_be_moved=distance < EXISTING_ANY_TYPE_LIMIT
                    or (is_same_type and distance < EXISTING_SAME_TYPE_LIMIT),
                )
            )
    return warnings


def duplicate_names(area, name, exclude_id=None):
    """Boxes in use in the area already painted with this name."""
    return (
        NestBox.objects.in_use()
        .filter(area=area, name__iexact=name.strip())
        .exclude(pk=exclude_id)
    )


def suggested_batch_boxes(area, season):
    """Boxes in use without a confirmed check this season and not in another open batch."""
    return (
        NestBox.objects.in_use()
        .filter(area=area)
        .exclude(
            Exists(
                Check.objects.filter(
                    box=OuterRef("pk"), season=season, is_confirmed=True
                )
            )
        )
        .exclude(Exists(Batch.objects.filter(boxes=OuterRef("pk"), closed_at=None)))
    )


def season_state_counts(boxes):
    """[{area_id, planned, to_check, attention, done}] of the areas with any of
    `boxes`, a queryset `with_season_state()`; one aggregate query."""
    return list(
        boxes.exclude(season_state=None)
        .order_by()
        .values("area_id")
        .annotate(
            **{
                state: Count("pk", filter=Q(season_state=state))
                for state in SeasonState.values
            }
        )
    )
