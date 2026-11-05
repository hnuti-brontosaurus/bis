from collections import Counter

from nest_boxes.models import NestBox
from nest_boxes.old_import.dump import parse_dump
from nest_boxes.old_import.load import load
from nest_boxes.old_import.plan import TABLES, plan


def import_dump(text):
    """Replaces all nest box data with the old budky database, read from its
    Adminer SQL dump, and returns the report lines. Old users appear by id only."""
    report = []
    tables = parse_dump(text, TABLES)
    planned = plan(tables)
    result = load(planned, tables["users"])

    report.append("Areas and their units:")
    for name, choice in sorted(result["choices"].items()):
        report.append(f"  {name}: {choice.unit.abbreviation} ({choice.reason})")

    report.append("\nCounts:")
    statuses = Counter(box.get_status_display() for box in result["boxes"])
    ended = Counter(
        box.end_reason.slug if box.end_reason else "no reason"
        for box in result["boxes"]
        if box.status == NestBox.Status.ENDED
    )
    counts = {
        "areas": len(result["choices"]),
        "boxes": len(result["boxes"]),
        **{f"boxes {status}": n for status, n in statuses.items()},
        **{f"boxes ended as {reason}": n for reason, n in ended.items()},
        "checks": result["checks"],
        **planned.report,
        **result["report"],
        "budkař role, matched old users": result["managers"],
        "budkař role, newly added": result["new_managers"],
    }
    for label, count in counts.items():
        report.append(f"  {label}: {count}")

    report.append("\nNot decided automatically:")
    report.append(
        "  old users with data and no BIS account by email: "
        f"{', '.join(map(str, result['unmatched'])) or 'none'}"
    )
    report.append(
        "  deactivated old users with data, not given the role: "
        f"{', '.join(map(str, result['inactive'])) or 'none'}"
    )
    for what, old_ids in planned.undecided.items():
        ids = ", ".join(map(str, sorted(set(old_ids))))
        report.append(f"  {what}, old boxes: {ids}")
    return report
