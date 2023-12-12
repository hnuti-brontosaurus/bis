from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "game_book"
    verbose_name = "Sborník her"

    def ready(self):
        import game_book.signals

    class Meta:
        verbose_name_plural = "Sborník her"
