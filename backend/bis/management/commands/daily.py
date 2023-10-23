import logging
from datetime import date

from django.core.management import call_command
from django.core.management.base import BaseCommand

from bis import emails


def try_to_run(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except Exception as e:
        logging.exception(e)

class Command(BaseCommand):
    def handle(self, *args, **options):
        try_to_run(call_command, "create_categories")
        try_to_run(call_command, "update_dashboard_items")
        try_to_run(call_command, "record_history")
        try_to_run(call_command, "import_locations")
        try_to_run(call_command, "import_donations")
        try_to_run(emails.event_ended_notify_organizers)
        try_to_run(emails.event_not_closed_10_days)
        try_to_run(emails.event_not_closed_20_days)
        try_to_run(emails.event_end_participants_notification)
        try_to_run(emails.qualification_about_to_end)

        # weekly
        if date.today().weekday() == 0:
            try_to_run(emails.events_created_summary)

        # monthly
        if date.today().day == 1:
            try_to_run(call_command, "close_events")
            try_to_run(emails.notify_not_closed_events_summary)

