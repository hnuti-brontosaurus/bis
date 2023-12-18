from django.apps import AppConfig


class DonationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "donations"
    verbose_name = "Dary"

    def ready(self):
        import donations.signals

    class Meta:
        verbose_name_plural = "Dary"
