from django.db.models.signals import pre_save
from django.dispatch import receiver
from feedback.models import EventFeedback, FeedbackForm

from bis.models import User


@receiver(pre_save, sender=EventFeedback, dispatch_uid="set_feedback_form_user")
def set_feedback_form_user(instance: EventFeedback, **kwargs):
    instance.user = (
        instance.user
        or instance.email
        and User.objects.filter(all_emails__email=instance.email).first()
        or None
    )
