import shutil
from datetime import date

from bis import emails
from bis.helpers import try_to_run
from django.core.management import call_command
from django.core.management.base import BaseCommand
from login_code.models import LoginCode
from other.models import SavedFile


def check_disk_space():
    total, used, _free = shutil.disk_usage("/app/media")
    used = used / total * 100
    if used > 90:
        emails.text(
            ["bis@brontosaurus.cz", "lamanchy@gmail.com"],
            "BIS disk usage is high",
            f"{used}% today ;)",
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        try_to_run(call_command, "create_categories")
        try_to_run(call_command, "update_dashboard_items")
        try_to_run(call_command, "record_history")
        try_to_run(call_command, "import_locations")
        try_to_run(call_command, "import_donations")
        try_to_run(call_command, "set_unique_user_str")
        try_to_run(call_command, "set_date_joined")
        try_to_run(call_command, "export_events")
        try_to_run(SavedFile.remove_old)
        try_to_run(LoginCode.remove_expired)
        try_to_run(call_command, "clearsessions")
        try_to_run(call_command, "cleartokens")

        today = date.today()

        # weekly
        if today.weekday() == 0:
            try_to_run(check_disk_space)

        # monthly
        if today.day == 1:
            try_to_run(call_command, "archive_events")
