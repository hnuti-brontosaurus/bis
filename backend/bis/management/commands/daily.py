import logging
import shutil
from datetime import date

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

from bis import emails
from other.models import SavedFile


def try_to_run(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except Exception as e:
        logging.exception(
            e,
            extra={
                "fn": str(fn),
                "data": {
                    "args": args,
                    "kwargs": kwargs,
                },
            },
        )
        connection.close()  # Close stale connection to force reconnect on next query


def check_disk_space():
    total, used, free = shutil.disk_usage("/app/media")
    used = used / total * 100
    if used > 90:
        emails.text(
            ["bis@brontosaurus.cz", "lamanchy@gmail.com"],
            f"BIS disk usage is high",
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
        try_to_run(emails.event_not_closed_10_days)
        try_to_run(emails.event_not_closed_20_days)
        try_to_run(emails.send_automatic_feedback)
        try_to_run(emails.qualification_about_to_end)
        try_to_run(emails.qualification_ended)
        try_to_run(SavedFile.remove_old)

        today = date.today()
        # weekly
        if today.weekday() == 0:
            try_to_run(emails.events_summary)
            try_to_run(emails.opportunities_created_summary)
            try_to_run(check_disk_space)
            try_to_run(emails.expressed_engagement_in_feedback)

        # monthly
        if today.day == 1:
            try_to_run(call_command, "archive_events")

        day_of_year = (today.day, today.month)

        if day_of_year == (15, 10):
            try_to_run(emails.fill_memberships, call=1)
        if day_of_year == (27, 10):
            try_to_run(emails.fill_memberships, call=2)

        if day_of_year == (31, 1):
            try_to_run(emails.qualification_ends_this_year)

        if day_of_year in [
            (15, 1),
            (15, 3),
            (15, 5),
            (15, 9),
            (30, 11),
        ]:
            try_to_run(emails.send_opportunities_summary)
