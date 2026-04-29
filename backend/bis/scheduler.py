"""
Simple background scheduler that runs scheduled commands at fixed times Prague time.
This replaces django-q2 with a lightweight custom solution.
"""

import logging
import sys
import threading
import time
from datetime import datetime

from django.conf import settings

_scheduler_started = False
_lock = threading.Lock()


def get_memory_usage():
    """Get current memory usage from cgroup (for Docker containers)."""
    try:
        with open("/sys/fs/cgroup/memory.current") as f:
            current_bytes = int(f.read().strip())

        with open("/sys/fs/cgroup/memory.max") as f:
            max_value = f.read().strip()
            if max_value == "max":
                max_str = "unlimited"
            else:
                max_mb = int(max_value) / 1024 / 1024
                max_str = f"{max_mb:.1f} MB"

        current_mb = current_bytes / 1024 / 1024
        return f"{current_mb:.1f} MB", max_str
    except Exception:
        return None, None


def is_running_under_server():
    """Check if Django is running under gunicorn or runserver (not migrate, shell, etc.)"""
    # Check for gunicorn
    if "gunicorn" in sys.modules:
        return True

    # Check for runserver in command line args
    return len(sys.argv) > 1 and "runserver" in sys.argv[1]


def run_command(name):
    """Run a management command, logging success/failure."""
    from django.core.management import call_command

    logging.info("Running %s command...", name)
    try:
        call_command(name)
        logging.info("%s command completed successfully", name)
    except Exception as e:
        logging.exception("%s command failed: %s", name, e)


def scheduler_loop():
    """Main scheduler loop: nightly at 5:00, daily at 7:00 Prague time."""
    import zoneinfo

    tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
    logging.info(
        "Scheduler started: nightly at 5:00, daily at 7:00 %s",
        settings.TIME_ZONE,
    )

    while True:
        try:
            seconds_until_next_minute = 60 - datetime.now().second
            time.sleep(seconds_until_next_minute)

            now = datetime.now(tz)

            if now.minute == 0:
                current, limit = get_memory_usage()
                if current:
                    logging.info("Memory: %s / %s", current, limit)

            if now.hour == 5 and now.minute == 0:
                run_command("nightly")

            if now.hour == 7 and now.minute == 0:
                run_command("daily")

        except Exception as e:
            logging.exception("Scheduler error: %s", e)


def start_scheduler():
    """Start the background scheduler thread if not already running."""
    global _scheduler_started

    if not is_running_under_server():
        return

    with _lock:
        if _scheduler_started:
            return
        _scheduler_started = True

    thread = threading.Thread(target=scheduler_loop, daemon=True, name="bis-scheduler")
    thread.start()
    logging.info("Background scheduler thread started")
