from pathlib import Path

from django.apps import AppConfig
from django.utils.autoreload import autoreload_started


class BISConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bis"
    verbose_name = "Základní informace"

    def ready(self):
        import bis.signals  # noqa

        def watch_directories(sender, **kwargs):
            sender.watch_dir(Path(__file__).parent.parent / "translation", "**/*")

        autoreload_started.connect(watch_directories)

        self.setup_schedules()

    def setup_schedules(self):
        from django_q.models import Schedule

        Schedule.objects.update_or_create(
            name="daily_command",
            defaults={
                "func": "django.core.management.call_command",
                "args": "'daily'",
                "schedule_type": Schedule.CRON,
                "cron": "0 7 * * *",
            },
        )

    class Meta:
        verbose_name_plural = "Základní informace"
