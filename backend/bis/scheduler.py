"""
Simple background scheduler that runs the daily command at 7 AM Prague time.
This replaces django-q2 with a lightweight custom solution.
"""

import logging
import os
import sys
import threading
import time
from datetime import datetime

from django.conf import settings

_scheduler_started = False
_lock = threading.Lock()


def is_running_under_server():
    """Check if Django is running under gunicorn or runserver (not migrate, shell, etc.)"""
    # Check for gunicorn
    if "gunicorn" in sys.modules:
        return True

    # Check for runserver in command line args
    if len(sys.argv) > 1 and "runserver" in sys.argv[1]:
        return True

    return False


def run_daily_command():
    """Run the daily management command."""
    from django.core.management import call_command

    logging.info("Running daily command...")
    try:
        call_command("daily")
        logging.info("Daily command completed successfully")
    except Exception as e:
        logging.exception("Daily command failed: %s", e)


def scheduler_loop():
    """Main scheduler loop that checks time and runs daily tasks."""
    import zoneinfo

    tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
    last_run_date = None
    target_hour = 7  # Run at 7 AM

    logging.info(
        "Scheduler started, will run daily command at %d:00 %s",
        target_hour,
        settings.TIME_ZONE,
    )

    while True:
        try:
            now = datetime.now(tz)
            today = now.date()

            # Run if it's past target hour and we haven't run today
            if now.hour >= target_hour and last_run_date != today:
                last_run_date = today
                run_daily_command()

            time.sleep(60)

        except Exception as e:
            logging.exception("Scheduler error: %s", e)
            # Sleep a bit before retrying on error
            time.sleep(60)


def start_scheduler():
    """Start the background scheduler thread if not already running."""
    global _scheduler_started

    if not is_running_under_server():
        return

    with _lock:
        if _scheduler_started:
            return
        _scheduler_started = True

    thread = threading.Thread(
        target=scheduler_loop, daemon=True, name="daily-scheduler"
    )
    thread.start()
    logging.info("Background scheduler thread started")
