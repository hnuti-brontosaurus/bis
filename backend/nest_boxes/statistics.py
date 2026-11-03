"""Season figures as defined in the requirements, from confirmed checks only."""

from django.db.models import Count, Q
from nest_boxes.models import Area, Check, NestBox

Content = Check.Content
FIGURES = (
    "boxes",
    "cleaned",
    "inspected",
    "occupied",
    "bird_occupied",
    "previous_inspected",
    "previous_occupied",
    "to_repair",
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
        "to_repair": _per_area(
            NestBox.objects.in_use().filter(
                condition__in=[
                    NestBox.Condition.NEEDS_REPAIR,
                    NestBox.Condition.NEEDS_REPLACING,
                ]
            ),
            "area",
        ),
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
        "areas": areas,
        "total": {figure: sum(counts[figure].values()) for figure in FIGURES},
    }
