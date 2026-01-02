from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cookbook"
    verbose_name = "Kuchařka"

    def ready(self):
        import cookbook.signals  # noqa

    class Meta:
        verbose_name_plural = "Kuchařka"
