from django.apps import AppConfig


class BISConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bis"
    verbose_name = "Základní informace"

    def ready(self):
        import bis.signals

    class Meta:
        verbose_name_plural = "Základní informace"
