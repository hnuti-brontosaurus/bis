from django.contrib.gis.db.models import *
from phonenumber_field.modelfields import PhoneNumberField

from bis.models import User
from categories.models import PronounCategory
from common.abstract_models import BaseAddress, BaseContact
from event.models import Event, EventRegistration
from translation.translate import translate_model


@translate_model
class EventApplication(Model):
    event_registration = ForeignKey(
        EventRegistration, related_name="applications", on_delete=PROTECT
    )
    user = ForeignKey(
        User, related_name="applications", on_delete=PROTECT, null=True, blank=True
    )
    states = [
        ("pending", "Čeká na schválení"),
        ("queued", "Náhradník"),
        ("cancelled", "Zrušena"),
        ("rejected", "Zamítnuta"),
        ("approved", "Potvrzena"),
    ]
    state = CharField(
        max_length=15,
        choices=states,
    )

    is_child_application = BooleanField(default=False)
    first_name = CharField(max_length=63)
    last_name = CharField(max_length=63)
    nickname = CharField(max_length=63, blank=True)
    phone = PhoneNumberField(blank=True)
    email = EmailField(blank=True, null=True)
    birthday = DateField(blank=True, null=True)
    health_issues = TextField(blank=True)
    pronoun = ForeignKey(
        PronounCategory,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="applications",
    )

    created_at = DateTimeField(auto_now_add=True)
    note = TextField(blank=True)
    internal_note = TextField(blank=True)
    paid_for = BooleanField(default=False)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"Přihláška na akci"

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(event_registration__event__in=events)

    def has_edit_permission(self, user):
        return self.event_registration.has_edit_permission(user)


@translate_model
class EventApplicationClosePerson(BaseContact):
    application = OneToOneField(
        EventApplication, related_name="close_person", on_delete=CASCADE
    )


@translate_model
class EventApplicationAddress(BaseAddress):
    application = OneToOneField(
        EventApplication, related_name="address", on_delete=CASCADE
    )


@translate_model
class Questionnaire(Model):
    # one-to-one relationship to event
    # holds relations to its questions and answers
    event_registration = OneToOneField(
        EventRegistration, on_delete=CASCADE, related_name="questionnaire"
    )
    introduction = TextField(blank=True)
    after_submit_text = TextField(blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return "Dotazník"

    def has_edit_permission(self, user):
        return not hasattr(
            self, "event_registration"
        ) or self.event_registration.has_edit_permission(user)


@translate_model
class Question(Model):
    question = CharField(max_length=255)
    data = JSONField(default=dict)
    is_required = BooleanField(default=True)
    order = PositiveIntegerField(default=0)
    questionnaire = ForeignKey(
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
class Answer(Model):
    # holds answer for specific question
    question = ForeignKey(Question, on_delete=CASCADE, related_name="answers")
    application = ForeignKey(
        EventApplication, on_delete=CASCADE, related_name="answers"
    )
    answer = TextField()
    data = JSONField(default=dict)

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
