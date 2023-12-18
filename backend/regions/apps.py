from django.apps import AppConfig


class BISConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "regions"
    verbose_name = "Kraje a PSČ"

    # def ready(self):
    #     import other.signals

    class Meta:
        verbose_name_plural = "Ostatní"
