from bis.models import User
from categories.models import PronounCategory
from common.abstract_models import BaseAddress, BaseContact
from django.contrib.gis.db.models import *
from event.models import Event, EventRecord, EventRegistration
from phonenumber_field.modelfields import PhoneNumberField
from translation.translate import translate_model


@translate_model
class EventFeedback(Model):
    event_record = ForeignKey(EventRecord, related_name="feedbacks", on_delete=PROTECT)
    user = ForeignKey(
        User, related_name="feedbacks", on_delete=PROTECT, null=True, blank=True
    )
    name = CharField(max_length=63, blank=True)
    email = EmailField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    note = TextField(blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"Zpětná vazba k akci"

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(event_record__event__in=events)

    def has_edit_permission(self, user):
        return self.event_record.has_edit_permission(user)


@translate_model
class FeedbackForm(Model):
    event_record = OneToOneField(
        EventRecord, on_delete=CASCADE, related_name="feedback_form"
    )
    introduction = TextField(blank=True)
    after_submit_text = TextField(blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return "Formulář zpětné vazby"

    def has_edit_permission(self, user):
        return not hasattr(
            self, "event_record"
        ) or self.event_record.has_edit_permission(user)


@translate_model
class Inquiry(Model):
    inquiry = CharField(max_length=255)
    data = JSONField(default=dict)
    is_required = BooleanField(default=True)
    order = PositiveIntegerField(default=0)
    feedback_form = ForeignKey(
        FeedbackForm, on_delete=CASCADE, related_name="inquiries"
    )

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.inquiry

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(feedback_form__event_record__event__in=events)

    def has_edit_permission(self, user):
        return self.feedback_form.has_edit_permission(user)


@translate_model
class Reply(Model):
    inquiry = ForeignKey(Inquiry, on_delete=CASCADE, related_name="replies")
    feedback = ForeignKey(EventFeedback, on_delete=CASCADE, related_name="replies")
    reply = TextField()
    data = JSONField(default=dict)

    class Meta:
        ordering = ("inquiry__order",)

    def __str__(self):
        return f"Odpověď na otázku {self.inquiry}"

    def has_edit_permission(self, user):
        return False

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(feedback__event_record__event__in=events)
