from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cookbook_categories"
    verbose_name = "Kategorie kuchařky"

    def ready(self):
        import cookbook_categories.signals  # noqa

    class Meta:
        verbose_name_plural = "Kategorie kuchařky"
