from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand
from nest_boxes.models import NestBox
from nest_boxes.old_import.dump import parse_dump
from nest_boxes.old_import.load import load
from nest_boxes.old_import.plan import TABLES, plan


class Command(BaseCommand):
    help = (
        "Replaces all nest box data with the old budky database, read from its "
        "Adminer SQL dump. Prints old users by id only."
    )

    def add_arguments(self, parser):
        parser.add_argument("dump", type=Path)

    def handle(self, dump, **options):
        tables = parse_dump(dump.read_text(encoding="utf-8"), TABLES)
        planned = plan(tables)
        result = load(planned, tables["users"])

        self.stdout.write("Areas and their units:")
        for name, choice in sorted(result["choices"].items()):
            self.stdout.write(f"  {name}: {choice.unit.abbreviation} ({choice.reason})")

        self.stdout.write("\nCounts:")
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
            self.stdout.write(f"  {label}: {count}")

        self.stdout.write("\nNot decided automatically:")
        self.stdout.write(
            "  old users with data and no BIS account by email: "
            f"{', '.join(map(str, result['unmatched'])) or 'none'}"
        )
        self.stdout.write(
            "  deactivated old users with data, not given the role: "
            f"{', '.join(map(str, result['inactive'])) or 'none'}"
        )
        for what, old_ids in planned.undecided.items():
            ids = ", ".join(map(str, sorted(set(old_ids))))
            self.stdout.write(f"  {what}, old boxes: {ids}")
