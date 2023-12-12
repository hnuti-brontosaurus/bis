from django.db.models.signals import pre_save
from django.dispatch import receiver
from questionnaire.models import *


@receiver(pre_save, sender=EventApplication, dispatch_uid="set_event_application_user")
def set_event_application_user(instance: EventApplication, **kwargs):
    instance.user = (
        instance.user
        or instance.birthday
        and User.objects.filter(
            first_name=instance.first_name,
            last_name=instance.last_name,
            birthday=instance.birthday,
        ).first()
        or instance.email
        and User.objects.filter(all_emails__email=instance.email).first()
        or None
    )
