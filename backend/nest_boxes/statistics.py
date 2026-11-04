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


def boxes_in_season(season, types=()):
    """Installed before the season ended, not retired before it started, needing cleaning."""
    start, end = Check.season_start(season), Check.season_end(season)
    boxes = NestBox.objects.filter(type__in=types) if types else NestBox.objects.all()
    return (
        boxes.exclude(status=NestBox.Status.PLANNED)
        .exclude(type__needs_cleaning=False)
        .filter(Q(installed_on=None) | Q(installed_on__lte=end))
        .filter(
            Q(ended_on=None) & ~Q(status=NestBox.Status.ENDED) | Q(ended_on__gte=start)
        )
    )


def confirmed_checks(season, types=()):
    return Check.objects.filter(
        season=season, is_confirmed=True, box__in=boxes_in_season(season, types)
    )


def inspected_checks(season, types=()):
    """Checks that tell what was inside: not found, unknown and unseen stay out."""
    return confirmed_checks(season, types).filter(
        found=Check.Found.FOUND,
        contents__overlap=[Content.NOTHING, Content.BIRD_NEST, Content.OTHER_ANIMAL],
    )


def _per_area(queryset, area_field):
    return dict(queryset.values_list(area_field).annotate(count=Count("pk")).order_by())


def _states_per_area(season, types):
    """This season's from the live season states, pending checks included; a past
    one's from its confirmed checks, since a past box's status and condition are
    gone, so there attention is what its check reported.
    """
    if season == Check.current_season():
        boxes = boxes_in_season(season, types).with_season_state()
        return {
            state: _per_area(boxes.filter(season_state=state), "area")
            for state in (SeasonState.DONE, SeasonState.ATTENTION)
        }
    checks = confirmed_checks(season, types)
    attention = (
        Q(found=Check.Found.NOT_FOUND)
        | Q(cleaning=Check.Cleaning.NOT_CLEANED)
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


OCCUPIED = [Content.BIRD_NEST, Content.OTHER_ANIMAL]


def _figures_per_area(season, types):
    return {
        "boxes": _per_area(boxes_in_season(season, types), "area"),
        "cleaned": _per_area(
            confirmed_checks(season, types).filter(cleaning=Check.Cleaning.CLEANED),
            "box__area",
        ),
        "inspected": _per_area(inspected_checks(season, types), "box__area"),
        "occupied": _per_area(
            inspected_checks(season, types).filter(contents__overlap=OCCUPIED),
            "box__area",
        ),
        "bird_occupied": _per_area(
            inspected_checks(season, types).filter(
                contents__contains=[Content.BIRD_NEST]
            ),
            "box__area",
        ),
    }


def _areas(area_ids):
    return Area.objects.filter(pk__in=area_ids).select_related("administration_unit")


def season_statistics(season, types=()):
    """Per area (rows with anything to show) and in total; raw counts, ratios are left to the reader."""
    counts = _figures_per_area(season, types)
    previous = _figures_per_area(season - 1, types)
    counts |= {
        "previous_inspected": previous["inspected"],
        "previous_occupied": previous["occupied"],
        **_states_per_area(season, types),
    }
    area_ids = set().union(*counts.values())
    areas = [
        {"area": area, **{figure: counts[figure].get(area.pk, 0) for figure in FIGURES}}
        for area in _areas(area_ids)
    ]
    return {
        "season": season,
        "seasons": _seasons(),
        "areas": areas,
        "total": {figure: sum(counts[figure].values()) for figure in FIGURES},
    }


SEASON_FIGURES = ("boxes", "cleaned", "inspected", "occupied", "bird_occupied")


def statistics_by_season(types=()):
    """Every season's figures per area, aligned with `seasons`, newest first."""
    seasons = _seasons()
    counts = [_figures_per_area(season, types) for season in seasons]
    area_ids = set().union(*(per_area for each in counts for per_area in each.values()))

    def figures_of(pk):
        return [
            {figure: each[figure].get(pk, 0) for figure in SEASON_FIGURES}
            for each in counts
        ]

    return {
        "seasons": seasons,
        "areas": [
            {"area": area, "seasons": figures_of(area.pk)} for area in _areas(area_ids)
        ],
    }
