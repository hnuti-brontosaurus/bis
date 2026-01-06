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

    class Meta:
        verbose_name_plural = "Základní informace"
