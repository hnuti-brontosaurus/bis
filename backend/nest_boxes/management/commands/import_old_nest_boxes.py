from pathlib import Path

from django.core.management.base import BaseCommand
from nest_boxes.old_import.run import import_dump


class Command(BaseCommand):
    help = (
        "Replaces all nest box data with the old budky database, read from its "
        "Adminer SQL dump. Prints old users by id only."
    )

    def add_arguments(self, parser):
        parser.add_argument("dump", type=Path)

    def handle(self, dump, **options):
        for line in import_dump(dump.read_text(encoding="utf-8")):
            self.stdout.write(line)
