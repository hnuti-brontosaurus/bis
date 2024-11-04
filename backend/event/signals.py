from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from event.models import Event, EventPropagation


@receiver(post_save, sender=Event, dispatch_uid="add_main_organizer_as_organizer")
def add_main_organizer_as_organizer(instance: Event, **kwargs):
    if instance.main_organizer:
        instance.other_organizers.add(instance.main_organizer)


@receiver(pre_save, sender=Event, dispatch_uid="compute_duration_of_event")
def compute_duration_of_event(instance: Event, **kwargs):
    new_value = max((instance.end - instance.start).days + 1, 0)
    new_value *= instance.number_of_sub_events

    if instance.duration != new_value:
        instance.duration = new_value


# @receiver(post_save, sender=Event, dispatch_uid='send_event_created_email')
# def send_event_created_email(instance: Event, created, **kwargs):
#     email_text()
#     if instance.main_organizer: instance.other_organizers.add(instance.main_organizer)
