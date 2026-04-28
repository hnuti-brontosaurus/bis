from django.contrib.gis.db import models as m
from django.db.models import CASCADE, PROTECT

from bis.models import User
from event.models import Event
from translation.translate import translate_model


@translate_model
class EventFeedback(m.Model):
    event = m.ForeignKey(Event, related_name="feedbacks", on_delete=PROTECT)
    user = m.ForeignKey(
        User, related_name="feedbacks", on_delete=PROTECT, null=True, blank=True
    )
    name = m.CharField(max_length=63, blank=True)
    email = m.EmailField(blank=True, null=True)
    created_at = m.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return "Zpětná vazba k akci"

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(event__in=events)

    def has_edit_permission(self, user):
        return self.event.has_edit_permission(user)


@translate_model
class FeedbackForm(m.Model):
    event = m.OneToOneField(Event, related_name="feedback_form", on_delete=CASCADE)
    email_content = m.TextField(blank=True)
    introduction = m.TextField(blank=True)
    after_submit_text = m.TextField(blank=True)
    sent_at = m.DateField(null=True, blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return "Formulář zpětné vazby"

    def has_edit_permission(self, user):
        return self.event.has_edit_permission(user)


@translate_model
class Inquiry(m.Model):
    inquiry = m.CharField(max_length=255)
    slug = m.SlugField(blank=True, max_length=255)
    data = m.JSONField(default=dict)
    is_required = m.BooleanField(default=True)
    order = m.PositiveIntegerField(default=0)
    feedback_form = m.ForeignKey(
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
class Reply(m.Model):
    inquiry = m.ForeignKey(Inquiry, on_delete=CASCADE, related_name="replies")
    feedback = m.ForeignKey(EventFeedback, on_delete=CASCADE, related_name="replies")
    reply = m.TextField()
    value = m.JSONField(default=None, null=True)
    data = m.JSONField(default=dict)

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
