from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "feedback"
    verbose_name = "Zpětné vazby"

    def ready(self):
        import feedback.signals  # noqa

    class Meta:
        verbose_name_plural = "Zpětné vazby"
