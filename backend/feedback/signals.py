from bis.models import User
from common.sensitivity import classify_after_save, reset_sensitivity
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from feedback.models import EventFeedback, Inquiry


@receiver(pre_save, sender=EventFeedback, dispatch_uid="set_feedback_form_user")
def set_feedback_form_user(instance: EventFeedback, **kwargs):
    instance.user = (
        instance.user
        or (
            instance.email
            and User.objects.filter(all_emails__email=instance.email).first()
        )
        or None
    )


@receiver(pre_save, sender=Inquiry, dispatch_uid="reset_inquiry_sensitivity")
def reset_inquiry_sensitivity(instance: Inquiry, **kwargs):
    reset_sensitivity(instance, "inquiry")


@receiver(post_save, sender=Inquiry, dispatch_uid="classify_inquiry")
def classify_inquiry(instance: Inquiry, **kwargs):
    classify_after_save(instance, "inquiry")
