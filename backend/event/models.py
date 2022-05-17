from os.path import basename

from django.contrib import admin
from django.contrib.gis.db.models import *
from django.db.models import Q
from django.utils.safestring import mark_safe

from administration_units.models import AdministrationUnit
from bis.models import Location, User
from categories.models import GrantCategory, PropagationIntendedForCategory, DietCategory, \
    EventCategory, EventProgramCategory
from translation.translate import translate_model


@translate_model
class Event(Model):
    # general
    name = CharField(max_length=63)
    is_canceled = BooleanField(default=False)
    start = DateTimeField()
    end = DateField()
    location = ForeignKey(Location, on_delete=CASCADE, related_name='events', null=True)

    category = ForeignKey(EventCategory, on_delete=CASCADE, related_name='events')
    program = ForeignKey(EventProgramCategory, on_delete=CASCADE, related_name='events')

    administration_unit = ForeignKey(AdministrationUnit, on_delete=CASCADE, related_name='events')
    main_organizer = ForeignKey(User, on_delete=CASCADE, related_name='events_where_was_as_main_organizer', null=True)
    other_organizers = ManyToManyField(User, related_name='events_where_was_as_other_organizer', blank=True)

    is_internal = BooleanField(default=False)
    number_of_sub_events = PositiveIntegerField(default=1)
    internal_note = TextField(blank=True)

    _import_id = CharField(max_length=15, default='')

    class Meta:
        ordering = '-start',
        app_label = 'bis'

    def __str__(self):
        return self.name

    @classmethod
    def filter_queryset(cls, queryset, user):
        if user.can_see_all:
            return queryset

        return queryset.filter(
            Q(administration_unit__board_members=user) |
            Q(main_organizer=user) |
            Q(other_organizers=user) |
            Q(record__participants=user)
        ).distinct()


@translate_model
class EventFinance(Model):
    event = OneToOneField(Event, related_name='finance', on_delete=CASCADE)

    grant_category = ForeignKey(GrantCategory, on_delete=CASCADE, related_name='events', null=True, blank=True)
    grant_amount = PositiveIntegerField(null=True, blank=True)
    total_event_cost = PositiveIntegerField(null=True, blank=True)
    budget = FileField(upload_to='budgets', blank=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'Finance k události {self.event}'


@translate_model
class EventPropagation(Model):
    event = OneToOneField(Event, related_name='propagation', on_delete=CASCADE)

    is_shown_on_web = BooleanField()

    minimum_age = PositiveIntegerField(null=True, blank=True)
    maximum_age = PositiveIntegerField(null=True, blank=True)
    cost = PositiveIntegerField()
    intended_for = ForeignKey(PropagationIntendedForCategory, on_delete=CASCADE, related_name='events')
    accommodation = CharField(max_length=255)
    diet = ForeignKey(DietCategory, on_delete=CASCADE, related_name='events')
    organizers = CharField(max_length=255)
    web_url = URLField(blank=True)
    _contact_url = URLField(blank=True)

    invitation_text_introduction = TextField()
    invitation_text_practical_information = TextField()
    invitation_text_work_description = TextField()
    invitation_text_about_us = TextField(blank=True)
    # propagation_images as Model below

    contact_person = ForeignKey(User, on_delete=CASCADE, related_name='events_where_was_as_contact_person', null=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'Propagace k události {self.event}'


@translate_model
class VIPEventPropagation(Model):
    event_propagation = OneToOneField(EventPropagation, related_name='vip_propagation', on_delete=CASCADE)

    goals_of_event = TextField()
    program = TextField()
    short_invitation_text = TextField(max_length=200)

    rover_propagation = BooleanField(default=False)

    working_hours = PositiveSmallIntegerField()
    working_days = PositiveSmallIntegerField()


@translate_model
class EventRegistration(Model):
    event = OneToOneField(Event, related_name='registration', on_delete=CASCADE)

    is_registration_required = BooleanField(default=True)
    is_event_full = BooleanField(default=False)

    # filled answers as part of questionary

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'Registrace k události {self.event}'


@translate_model
class EventRecord(Model):
    event = OneToOneField(Event, related_name='record', on_delete=CASCADE)

    total_hours_worked = PositiveIntegerField(null=True, blank=True)
    comment_on_work_done = TextField(blank=True)
    has_attendance_list = BooleanField(default=True)
    participants = ManyToManyField(User, 'participated_in_events', blank=True)
    number_of_participants = PositiveIntegerField(null=True, blank=True)
    number_of_participants_under_26 = PositiveIntegerField(null=True, blank=True)

    # photos as Model below

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'Záznam k události {self.event}'


@translate_model
class EventPropagationImage(Model):
    propagation = ForeignKey(EventPropagation, on_delete=CASCADE, related_name='propagation_images')
    order = PositiveIntegerField()
    image = ImageField(upload_to='event_propagation_images')

    @admin.display(description='Náhled')
    def image_tag(self):
        return mark_safe(f'<img style="max-height: 10rem; max-width: 20rem" src="{self.image.url}" />')

    class Meta:
        ordering = 'order',

    def __str__(self):
        return basename(self.image.name)


@translate_model
class EventPhoto(Model):
    record = ForeignKey(EventRecord, on_delete=CASCADE, related_name='photos')
    photo = ImageField(upload_to='event_photos')

    @admin.display(description='Náhled')
    def photo_tag(self):
        return mark_safe(f'<img style="max-height: 10rem; max-width: 20rem" src="{self.photo.url}" />')

    class Meta:
        ordering = 'id',

    def __str__(self):
        return basename(self.photo.name)