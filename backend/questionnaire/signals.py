from bis.models import User
from common.sensitivity import classify_after_save, reset_sensitivity
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from questionnaire.models import EventApplication, Question


@receiver(pre_save, sender=EventApplication, dispatch_uid="set_event_application_user")
def set_event_application_user(instance: EventApplication, **kwargs):
    instance.user = (
        instance.user
        or (
            instance.birthday
            and User.objects.filter(
                first_name=instance.first_name,
                last_name=instance.last_name,
                birthday=instance.birthday,
            ).first()
        )
        or (
            instance.email
            and User.objects.filter(all_emails__email=instance.email).first()
        )
        or None
    )


@receiver(pre_save, sender=Question, dispatch_uid="reset_question_sensitivity")
def reset_question_sensitivity(instance: Question, **kwargs):
    reset_sensitivity(instance, "question")


@receiver(post_save, sender=Question, dispatch_uid="classify_question")
def classify_question(instance: Question, **kwargs):
    classify_after_save(instance, "question")
