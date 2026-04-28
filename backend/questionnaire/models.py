from django.contrib.gis.db import models as m
from django.db.models import CASCADE, PROTECT
from phonenumber_field.modelfields import PhoneNumberField

from bis.models import User
from categories.models import PronounCategory
from common.abstract_models import BaseAddress, BaseContact
from event.models import Event, EventRegistration
from translation.translate import translate_model


@translate_model
class EventApplication(m.Model):
    event_registration = m.ForeignKey(
        EventRegistration, related_name="applications", on_delete=PROTECT
    )
    user = m.ForeignKey(
        User, related_name="applications", on_delete=PROTECT, null=True, blank=True
    )
    states = [
        ("pending", "Čeká na schválení"),
        ("queued", "Náhradník"),
        ("cancelled", "Zrušena"),
        ("rejected", "Zamítnuta"),
        ("approved", "Potvrzena"),
    ]
    state = m.CharField(
        max_length=15,
        choices=states,
    )

    is_child_application = m.BooleanField(default=False)
    first_name = m.CharField(max_length=63)
    last_name = m.CharField(max_length=63)
    nickname = m.CharField(max_length=63, blank=True)
    phone = PhoneNumberField(blank=True)
    email = m.EmailField(blank=True, null=True)
    birthday = m.DateField(blank=True, null=True)
    health_issues = m.TextField(blank=True)
    pronoun = m.ForeignKey(
        PronounCategory,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="applications",
    )

    created_at = m.DateTimeField(auto_now_add=True)
    applicant_note = m.TextField(blank=True)
    paid_for = m.BooleanField(default=False)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return "Přihláška na akci"

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(event_registration__event__in=events)

    def has_edit_permission(self, user):
        return self.event_registration.has_edit_permission(user)


@translate_model
class EventApplicationClosePerson(BaseContact):
    application = m.OneToOneField(
        EventApplication, related_name="close_person", on_delete=CASCADE
    )


@translate_model
class EventApplicationAddress(BaseAddress):
    application = m.OneToOneField(
        EventApplication, related_name="address", on_delete=CASCADE
    )


@translate_model
class Questionnaire(m.Model):
    # one-to-one relationship to event
    # holds relations to its questions and answers
    event_registration = m.OneToOneField(
        EventRegistration, on_delete=CASCADE, related_name="questionnaire"
    )
    introduction = m.TextField(blank=True)
    after_submit_text = m.TextField(blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return "Dotazník"

    def has_edit_permission(self, user):
        return not hasattr(
            self, "event_registration"
        ) or self.event_registration.has_edit_permission(user)


@translate_model
class Question(m.Model):
    question = m.CharField(max_length=255)
    data = m.JSONField(default=dict)
    is_required = m.BooleanField(default=True)
    order = m.PositiveIntegerField(default=0)
    questionnaire = m.ForeignKey(
        Questionnaire, on_delete=CASCADE, related_name="questions"
    )

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.question

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(questionnaire__event_registration__event__in=events)

    def has_edit_permission(self, user):
        return self.questionnaire.has_edit_permission(user)


@translate_model
class Answer(m.Model):
    # holds answer for specific question
    question = m.ForeignKey(Question, on_delete=CASCADE, related_name="answers")
    application = m.ForeignKey(
        EventApplication, on_delete=CASCADE, related_name="answers"
    )
    answer = m.TextField()
    data = m.JSONField(default=dict)

    class Meta:
        ordering = ("question__order",)

    def __str__(self):
        return f"Odpověď na otázku {self.question}"

    def has_edit_permission(self, user):
        return False

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(application__event_registration__event__in=events)
