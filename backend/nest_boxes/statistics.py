"""Season figures as defined in the requirements, from confirmed checks only."""

from django.db.models import Count, Min, Q
from nest_boxes.models import Area, Check, NestBox, SeasonState

Content = Check.Content
FIGURES = (
    "boxes",
    "cleaned",
    "inspected",
    "occupied",
    "bird_occupied",
    "previous_inspected",
    "previous_occupied",
    # The pie of the map of areas; what is left of `boxes` is still to check
    "done",
    "attention",
)


def boxes_in_season(season):
    """Installed before the season ended, not retired before it started, needing cleaning."""
    start, end = Check.season_start(season), Check.season_end(season)
    return (
        NestBox.objects.filter(is_confirmed=True)
        .exclude(status__in=[NestBox.Status.PLANNED, NestBox.Status.CANCELLED])
        .exclude(type__needs_cleaning=False)
        .filter(Q(installed_on=None) | Q(installed_on__lte=end))
        .filter(
            Q(ended_on=None) & ~Q(status=NestBox.Status.ENDED) | Q(ended_on__gte=start)
        )
    )


def inspected_checks(season):
    """Checks that saw inside the box: not found, couldn't open and unknown stay out."""
    return Check.objects.filter(
        season=season,
        is_confirmed=True,
        found=Check.Found.FOUND,
        box__in=boxes_in_season(season),
        contents__overlap=[Content.NOTHING, Content.BIRD_NEST, Content.OTHER_ANIMAL],
    ).exclude(cleaning=Check.Cleaning.COULD_NOT_OPEN)


def _per_area(queryset, area_field):
    return dict(queryset.values_list(area_field).annotate(count=Count("pk")).order_by())


def _states_per_area(season):
    """This season's from the live season states, pending checks included; a past
    one's from its confirmed checks, since a past box's status and condition are
    gone, so there attention is what its check reported.
    """
    if season == Check.current_season():
        boxes = boxes_in_season(season).with_season_state()
        return {
            state: _per_area(boxes.filter(season_state=state), "area")
            for state in (SeasonState.DONE, SeasonState.ATTENTION)
        }
    checks = Check.objects.filter(
        season=season, is_confirmed=True, box__in=boxes_in_season(season)
    )
    attention = (
        Q(found=Check.Found.NOT_FOUND)
        | Q(cleaning__in=[Check.Cleaning.NOT_CLEANED, Check.Cleaning.COULD_NOT_OPEN])
        | Q(
            box_left__in=[
                Check.BoxLeft.NEEDS_REPAIR,
                Check.BoxLeft.NEEDS_REPLACING,
                Check.BoxLeft.TAKEN_DOWN,
            ]
        )
    )
    return {
        SeasonState.DONE: _per_area(
            checks.filter(found=Check.Found.FOUND).exclude(attention), "box__area"
        ),
        SeasonState.ATTENTION: _per_area(checks.filter(attention), "box__area"),
    }


def default_season():
    """The season shown unless another is asked for: the current one once anything
    is checked in it, until then the one before, which a new season on 1 July
    would otherwise replace with zeros.

    Any check counts, pending or imported too: a pending one already shows in the
    current season's pie, an imported one is field work done in the old app.
    """
    current = Check.current_season()
    return current if Check.objects.filter(season=current).exists() else current - 1


def _seasons():
    """The newest first, from the first season anything was checked in, or else the default one."""
    current = Check.current_season()
    first = Check.objects.aggregate(first=Min("season"))["first"] or default_season()
    return list(range(current, first - 1, -1))


def season_statistics(season):
    """Per area (rows with anything to show) and in total; raw counts, ratios are left to the reader."""
    occupied = [Content.BIRD_NEST, Content.OTHER_ANIMAL]
    counts = {
        "boxes": _per_area(boxes_in_season(season), "area"),
        "cleaned": _per_area(
            Check.objects.filter(
                season=season,
                is_confirmed=True,
                cleaning=Check.Cleaning.CLEANED,
                box__in=boxes_in_season(season),
            ),
            "box__area",
        ),
        "inspected": _per_area(inspected_checks(season), "box__area"),
        "occupied": _per_area(
            inspected_checks(season).filter(contents__overlap=occupied), "box__area"
        ),
        "bird_occupied": _per_area(
            inspected_checks(season).filter(contents__contains=[Content.BIRD_NEST]),
            "box__area",
        ),
        "previous_inspected": _per_area(inspected_checks(season - 1), "box__area"),
        "previous_occupied": _per_area(
            inspected_checks(season - 1).filter(contents__overlap=occupied),
            "box__area",
        ),
        **_states_per_area(season),
    }
    area_ids = set().union(*counts.values())
    areas = [
        {"area": area, **{figure: counts[figure].get(area.pk, 0) for figure in FIGURES}}
        for area in Area.objects.filter(pk__in=area_ids).select_related(
            "administration_unit"
        )
    ]
    return {
        "season": season,
        "seasons": _seasons(),
        "areas": areas,
        "total": {figure: sum(counts[figure].values()) for figure in FIGURES},
    }
