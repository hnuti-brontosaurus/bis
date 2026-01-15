from categories.models import PronounCategory
from common.abstract_models import BaseAddress, BaseContact
from django.contrib.gis.db.models import *
from event.models import Event, EventRecord, EventRegistration
from phonenumber_field.modelfields import PhoneNumberField
from translation.translate import translate_model

from bis.models import User


@translate_model
class EventFeedback(Model):
    event = ForeignKey(Event, related_name="feedbacks", on_delete=PROTECT)
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
        return queryset.filter(event__in=events)

    def has_edit_permission(self, user):
        return self.event.has_edit_permission(user)


@translate_model
class FeedbackForm(Model):
    event = OneToOneField(Event, related_name="feedback_form", on_delete=PROTECT)
    introduction = TextField(blank=True)
    after_submit_text = TextField(blank=True)
    sent_at = DateField(null=True, blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return "Formulář zpětné vazby"

    def has_edit_permission(self, user):
        return self.event.has_edit_permission(user)


@translate_model
class Inquiry(Model):
    inquiry = CharField(max_length=255)
    slug = SlugField(blank=True, max_length=255)
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
        return queryset.filter(feedback_form__event__in=events)

    def has_edit_permission(self, user):
        return self.feedback_form.has_edit_permission(user)


@translate_model
class Reply(Model):
    inquiry = ForeignKey(Inquiry, on_delete=CASCADE, related_name="replies")
    feedback = ForeignKey(EventFeedback, on_delete=CASCADE, related_name="replies")
    reply = TextField()
    value = JSONField(default=None, null=True)
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
        return queryset.filter(feedback__event__in=events)
