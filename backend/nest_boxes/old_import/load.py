"""Writes a plan of the old database into the nest box models, replacing what is there."""

from collections import Counter
from dataclasses import dataclass
from datetime import date

from administration_units.models import AdministrationUnit, BrontosaurusMovement
from bis.models import User
from categories.models import (
    NestBoxEndReason,
    NestBoxNotCleanedReason,
    NestBoxOccupant,
    NestBoxType,
)
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import make_aware
from event.models import Event
from nest_boxes.boxes import suggest_type
from nest_boxes.models import Area, Batch, Check, NestBox, NestBoxHistory
from nest_boxes.old_import.plan import ENTRIES_SINCE, OLD_TYPES
from regions.models import Region

HEADQUARTERS_CATEGORY = "headquarter"
ACTIVITY_SINCE = date(2022, 1, 1)
# Sitting on a unit's board says more than organizing one of its events
BOARD_MEMBER_WEIGHT = 5
ELEVATION_SOURCE = "stará databáze"


@dataclass
class UnitChoice:
    unit: AdministrationUnit
    reason: str


def match_users(old_users):
    """{old user id: BIS user} by any of the BIS user's emails, ignoring case."""
    matched = {}
    for row in old_users:
        user = User.objects.filter(
            all_emails__email__iexact=row["email"].strip()
        ).first()
        if user:
            matched[int(row["id"])] = user
    return matched


def unit_activity(user):
    """Per active unit: events organized since ACTIVITY_SINCE, plus board membership.

    Headquarters is left out: its events are national, so they say nothing about
    who looks after a place. It is only the fallback.
    """
    scores = Counter()
    units = AdministrationUnit.objects.filter(existed_till=None).exclude(
        category__slug=HEADQUARTERS_CATEGORY
    )
    events = (
        Event.objects.filter(start__gte=ACTIVITY_SINCE)
        .filter(Q(main_organizer=user) | Q(other_organizers=user))
        .distinct()
    )
    for unit_id in units.filter(events__in=events).values_list("pk", flat=True):
        scores[unit_id] += 1
    for unit_id in units.filter(board_members=user).values_list("pk", flat=True):
        scores[unit_id] += BOARD_MEMBER_WEIGHT
    return scores


def choose_unit(entries, activities, headquarters):
    """The unit the area's recent data enterers are most active in, weighted by
    their entries; all-time enterers when no recent one is known to BIS."""
    recent, all_time = entries
    for counter, period in (
        (recent, f"since {ENTRIES_SINCE}"),
        (all_time, "all years"),
    ):
        if choice := _choose_unit(counter, activities, period):
            return choice
    enterers = ", ".join(map(str, all_time)) or "nobody"
    return UnitChoice(
        headquarters, f"no BIS activity of old users {enterers}: headquarters"
    )


def _choose_unit(entries, activities, period):
    total = sum(entries.values())
    scores = Counter()
    considered = []
    for old_user, count in entries.most_common():
        activity = activities.get(old_user)
        if not activity:
            continue
        considered.append(f"{old_user} ({round(100 * count / total)} %)")
        weight = count / total / sum(activity.values())
        for unit_id, score in activity.items():
            scores[unit_id] += weight * score
    if not scores:
        return None
    unit_id, score = scores.most_common(1)[0]
    share = round(100 * score / sum(scores.values()))
    return UnitChoice(
        AdministrationUnit.objects.get(pk=unit_id),
        f"old users {', '.join(considered)} {period}; {share} % of their activity",
    )


def _type(box, types):
    if box.hole:
        if suggested := suggest_type(*box.hole):
            return suggested, "hole"
    if slug := OLD_TYPES.get(box.old_type):
        return types[slug], "old type"
    return None, "unknown"


def wipe():
    NestBoxHistory.objects.all().delete()
    Check.objects.all().delete()
    Batch.objects.all().delete()
    NestBox.objects.all().delete()
    Area.objects.all().delete()


@transaction.atomic
def load(plan, old_users):
    report = Counter()
    wipe()
    users = match_users(old_users)
    headquarters = AdministrationUnit.objects.get(category__slug=HEADQUARTERS_CATEGORY)
    named_units = {
        name: AdministrationUnit.objects.get(name__icontains=name)
        for name in plan.unit_names
    }

    activities = {old_user: unit_activity(user) for old_user, user in users.items()}
    choices = {
        area_id: choose_unit(plan.entries[area_id], activities, headquarters)
        for area_id in plan.areas
    }
    areas = {
        area_id: Area.objects.create(
            name=name, administration_unit=choices[area_id].unit
        )
        for area_id, name in plan.areas.items()
    }

    types = {box_type.slug: box_type for box_type in NestBoxType.objects.all()}
    end_reasons = {reason.slug: reason for reason in NestBoxEndReason.objects.all()}
    not_cleaned_reasons = {
        reason.slug: reason for reason in NestBoxNotCleanedReason.objects.all()
    }
    occupants = {occupant.slug: occupant for occupant in NestBoxOccupant.objects.all()}

    boxes = []
    for planned in plan.boxes:
        box_type, source = _type(planned, types)
        report[f"types from {source}"] += 1
        shape, size = planned.hole or ("", None)
        boxes.append(
            NestBox(
                area=areas[planned.old_area_id],
                name=planned.name,
                previous_names=planned.previous_names,
                status=planned.status,
                condition=planned.condition,
                location=Point(planned.location[1], planned.location[0], srid=4326),
                elevation=planned.elevation,
                elevation_source=ELEVATION_SOURCE if planned.elevation else "",
                type=box_type,
                hole_shape=shape,
                hole_size=size,
                opening=planned.opening,
                material=planned.material,
                predator_guard=planned.predator_guard,
                access_note=planned.access_note,
                owner_note=planned.owner_note,
                note=planned.note,
                installed_on=planned.installed_on,
                ended_on=planned.ended_on,
                end_reason=end_reasons[planned.end_reason]
                if planned.end_reason
                else None,
                is_verified=False,
                is_confirmed=True,
                old_id=planned.old_id,
                created_by=users.get(planned.old_user_id),
            )
        )
    NestBox.objects.bulk_create(boxes)
    for box, planned in zip(boxes, plan.boxes):
        box.created_at = make_aware(planned.created_at)
    NestBox.objects.bulk_update(boxes, ["created_at"])
    for region in Region.objects.all():
        NestBox.objects.filter(location__within=region.area).update(region=region)
    for area in areas.values():
        NestBox.recompute_distances(area.pk)

    checks, check_occupants = [], []
    for box, planned in zip(boxes, plan.boxes):
        for planned_check in planned.checks:
            reading = planned_check.reading
            made_at = make_aware(planned_check.made_at)
            check = Check(
                box=box,
                date=planned_check.date,
                season=Check.season_of(planned_check.date),
                made_at=made_at,
                entered_by=users.get(planned_check.old_user_id),
                is_confirmed=True,
                confirmed_at=made_at,
                cleaned_by=named_units.get(
                    planned_check.unit_name, box.area.administration_unit
                ),
                found=reading.found,
                cleaning=reading.cleaning,
                not_cleaned_reason=(
                    not_cleaned_reasons[reading.not_cleaned_reason]
                    if reading.not_cleaned_reason
                    else None
                ),
                contents=reading.contents,
                eggs_left=reading.eggs_left,
                dead_birds=reading.dead_birds,
                breeding_note=reading.breeding_note,
                box_left=reading.box_left,
                note=planned_check.note,
                is_historical=True,
            )
            checks.append(check)
            check_occupants += [
                Check.occupants.through(check=check, nestboxoccupant=occupants[slug])
                for slug in sorted(reading.occupants)
            ]
    Check.objects.bulk_create(checks)
    Check.occupants.through.objects.bulk_create(check_occupants)

    movement = BrontosaurusMovement.get()
    managers = {users[old] for old in plan.data_users if old in users}
    already = set(movement.nest_box_managers.all())
    movement.nest_box_managers.add(*managers)
    return {
        "report": report,
        "choices": {areas[area_id].name: choice for area_id, choice in choices.items()},
        "boxes": boxes,
        "checks": len(checks),
        "new_managers": len(managers - already),
        "managers": len(managers),
        "unmatched": sorted(plan.data_users - set(users)),
        "inactive": sorted(plan.inactive_users),
    }
