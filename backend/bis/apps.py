from pathlib import Path

from bis.email_validation import validate_email
from django.apps import AppConfig
from django.db.models import EmailField
from django.utils.autoreload import autoreload_started

# Runs at app-load time, before any model module is imported, so every EmailField
# in the project (including third-party apps') picks our validator up via its
# `default_validators` class attribute.
if validate_email not in EmailField.default_validators:
    EmailField.default_validators = [*EmailField.default_validators, validate_email]


class BISConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bis"
    verbose_name = "Základní informace"

    def ready(self):
        import bis.signals  # noqa

        def watch_directories(sender, **kwargs):
            sender.watch_dir(Path(__file__).parent.parent / "translation", "**/*")

        autoreload_started.connect(watch_directories)

        from bis.scheduler import start_scheduler

        start_scheduler()

    class Meta:
        verbose_name_plural = "Základní informace"
