from django.apps import AppConfig


class BISConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'administration_units'
    verbose_name = 'Administrativní jednotky'

    def ready(self):
        import administration_units.signals

    class Meta:
        verbose_name_plural = "Administrativní jednotky"