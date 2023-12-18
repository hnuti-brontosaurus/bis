from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "game_book_categories"
    verbose_name = "Kategorie sborníku her"

    def ready(self):
        import game_book_categories.signals

    class Meta:
        verbose_name_plural = "Kategorie sborníku her"
