from django.apps import AppConfig


class BISConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "opportunities"
    verbose_name = "Příležitost"

    def ready(self):
        import opportunities.signals

    class Meta:
        verbose_name_plural = "Příležitosti"
