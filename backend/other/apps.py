from django.apps import AppConfig


class BISConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "other"
    verbose_name = "Ostatní"

    # def ready(self):
    #     import other.signals

    class Meta:
        verbose_name_plural = "Ostatní"
