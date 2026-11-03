import json

from django.contrib.gis.geos import GEOSException, GEOSGeometry, Point
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils.timezone import localdate, now
from nest_boxes.boxes import confirm_box, update_box
from nest_boxes.models import Check, NestBox

# Keys of Check.box_changes. `location` is a GeoJSON point, `type` a
# NestBoxType id, `installed_on` an ISO date; `hung` marks a planned box hung.
BOX_CHANGE_FIELDS = (
    "name",
    "hole_shape",
    "hole_size",
    "type",
    "opening",
    "material",
    "location",
    "installed_on",
)
HUNG = "hung"
VERIFICATION_FIELDS = {"name", "location", "hole_shape", "hole_size", "type", "opening"}
RETURNABLE_STATUSES = (
    NestBox.Status.IN_USE,
    NestBox.Status.MISSING,
    NestBox.Status.TAKEN_DOWN,
)


class BatchClosed(Exception):
    pass


def _point(geojson):
    point = GEOSGeometry(json.dumps(geojson), srid=4326)
    if not isinstance(point, Point):
        raise ValueError("poloha musí být bod")
    return point


def parse_box_changes(box_changes):
    """Model values for Check.box_changes, raising ValidationError when invalid."""
    unknown = set(box_changes) - set(BOX_CHANGE_FIELDS) - {HUNG}
    if unknown:
        raise ValidationError({"box_changes": f"Neznámé položky: {sorted(unknown)}"})
    values = {}
    for name in BOX_CHANGE_FIELDS:
        if name not in box_changes:
            continue
        value = box_changes[name]
        field = NestBox._meta.get_field(name)
        try:
            if name == "location":
                values[name] = _point(value)
            elif field.is_relation:
                pk = field.clean(value, None)
                values[name] = (
                    None if pk is None else field.related_model.objects.get(pk=pk)
                )
            else:
                values[name] = field.clean(value, None)
        except (ValidationError, ValueError, TypeError, GEOSException) as error:
            raise ValidationError({"box_changes": f"{name}: {error}"})
    if HUNG in box_changes and not isinstance(box_changes[HUNG], bool):
        raise ValidationError({"box_changes": f"{HUNG}: musí být true nebo false"})
    return values


def _box_values(check):
    box = check.box
    values = parse_box_changes(check.box_changes)
    if box.status == NestBox.Status.PLANNED:
        if check.box_changes.get(HUNG):
            values["status"] = NestBox.Status.IN_USE
            values.setdefault("installed_on", check.date)
    elif box.status in RETURNABLE_STATUSES:
        if check.found == Check.Found.NOT_FOUND:
            values["status"] = NestBox.Status.MISSING
        elif check.found == Check.Found.FOUND:
            if check.box_left == Check.BoxLeft.TAKEN_DOWN:
                values["status"] = NestBox.Status.TAKEN_DOWN
            else:
                values["status"] = NestBox.Status.IN_USE
                if check.box_left:
                    values["condition"] = check.box_left
    if (
        check.found == Check.Found.FOUND
        and set(check.box_changes) >= VERIFICATION_FIELDS
    ):
        values["is_verified"] = True
    return values


@transaction.atomic
def confirm_check(check, user):
    """Confirms a check and applies it to its box: status, condition, box_changes."""
    check.is_confirmed = True
    check.confirmed_at = now()
    check.confirmed_by = user
    check.save()
    update_box(check.box, _box_values(check), user, check.date, check)


def _ensure_alone_in_season(check):
    rival = (
        Check.objects.filter(box=check.box, season=Check.season_of(check.date))
        .exclude(pk=check.pk)
        .first()
    )
    if rival:
        raise ValidationError(
            {"date": f"Budka už má v této sezóně kontrolu {rival.pk}, uprav tu."}
        )


@transaction.atomic
def enter_check(check, occupants, user):
    """A manager's own check: confirmed at once, unless it is entered into a batch."""
    _ensure_alone_in_season(check)
    check.entered_by = user
    check.save()
    check.occupants.set(occupants)
    if check.batch is None:
        confirm_check(check, user)
    else:
        check.batch.boxes.add(check.box)
    return check


@transaction.atomic
def edit_check(check, occupants, user):
    """A manager's edit. A confirmed check is applied to its box again when it is
    the box's latest, so correcting a mistake corrects the box too."""
    _ensure_alone_in_season(check)
    check.save()
    check.occupants.set(occupants)
    latest = Check.objects.filter(box=check.box).order_by("-date", "-made_at").first()
    if check.is_confirmed and latest == check:
        update_box(check.box, _box_values(check), user, check.date, check)
    return check


@transaction.atomic
def upsert_check(check, occupants):
    """Stores `check` unless it loses to the season's check already there.

    The check made later on the phone wins; a confirmed one is never replaced.
    Returns the check that is stored afterwards, which may be the old one.
    """
    stored = Check.objects.select_for_update().filter(pk=check.pk).first()
    if stored and (stored.is_confirmed or stored.made_at > check.made_at):
        return stored
    rival = (
        Check.objects.select_for_update()
        .filter(box=check.box, season=Check.season_of(check.date))
        .exclude(pk=check.pk)
        .first()
    )
    if rival:
        if rival.is_confirmed or rival.made_at >= check.made_at:
            return rival
        rival.delete()
    # The id is client-generated, so an unsaved instance can be a resend
    check.save(force_update=stored is not None)
    check.occupants.set(occupants)
    return check


def ensure_open(batch):
    if batch.closed_at is not None:
        raise BatchClosed


def submit_check(batch, check, occupants):
    """A volunteer's check through a batch link, left pending."""
    ensure_open(batch)
    if not batch.boxes.filter(pk=check.box_id).exists():
        raise PermissionDenied
    check.batch = batch
    check.is_confirmed = False
    check.confirmed_at = None
    check.confirmed_by = None
    return upsert_check(check, occupants)


@transaction.atomic
def submit_box(batch, box):
    """A box a volunteer adds through a batch link, unconfirmed and unverified."""
    ensure_open(batch)
    stored = NestBox.objects.filter(pk=box.pk).first()
    if stored and (stored.is_confirmed or stored.batch_id != batch.pk):
        raise PermissionDenied
    box.area = batch.area
    box.batch = batch
    box.status = NestBox.Status.IN_USE
    box.is_confirmed = False
    box.is_verified = False
    box.save(force_update=stored is not None)
    batch.boxes.add(box)
    return box


@transaction.atomic
def confirm_batch(batch, user):
    """Confirms the batch's new boxes and pending checks, and closes it."""
    today = localdate()
    for box in batch.new_boxes.filter(is_confirmed=False):
        confirm_box(box, user, today)
    for check in batch.checks.filter(is_confirmed=False).order_by("date", "made_at"):
        confirm_check(check, user)
    batch.confirmed_at = now()
    batch.confirmed_by = user
    batch.closed_at = batch.closed_at or batch.confirmed_at
    batch.save()


def close_batch(batch):
    """Stops the link taking checks; pending checks stay pending."""
    if batch.closed_at is None:
        batch.closed_at = now()
        batch.save()
