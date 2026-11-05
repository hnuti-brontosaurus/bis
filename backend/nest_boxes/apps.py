from django.apps import AppConfig


class NestBoxesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nest_boxes"
    verbose_name = "Budky"

    def ready(self):
        from nest_boxes import public_cache  # noqa: F401  registers the signals
