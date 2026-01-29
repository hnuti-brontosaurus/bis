from django.apps import AppConfig

from translation.translate import _


class BISConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "event"
    verbose_name = _("models.Event.name_plural")

    def ready(self):
        import event.signals

    class Meta:
        verbose_name_plural = _("models.Event.name_plural")
