from django.apps import AppConfig


class QuestionnaireConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "questionnaire"
    verbose_name = "Dotazníky"

    def ready(self):
        import questionnaire.signals

    class Meta:
        verbose_name_plural = "Dotazníky"
