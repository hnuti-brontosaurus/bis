from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "categories"
    verbose_name = "Kategorie"

    def ready(self):
        import categories.signals

    class Meta:
        verbose_name_plural = "Kategorie"
