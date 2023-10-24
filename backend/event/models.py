from os.path import basename

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import admin
from django.contrib.gis.db.models import *
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from phonenumber_field.modelfields import PhoneNumberField
from tinymce.models import HTMLField

from administration_units.models import AdministrationUnit
from bis import emails
from bis.helpers import permission_cache, update_roles, filter_queryset_with_multiple_or_queries, on_save
from bis.models import Location, User, Qualification
from categories.models import GrantCategory, EventIntendedForCategory, DietCategory, \
    EventCategory, EventProgramCategory, EventGroupCategory, EventTag
from common.abstract_models import BaseContact
from common.thumbnails import ThumbnailImageField
from translation.translate import translate_model


class EventDraft(Model):
    owner = ForeignKey(User, related_name='event_drafts', on_delete=CASCADE)
    data = JSONField()

    @permission_cache
    def has_edit_permission(self, user):
        return user == self.owner

    @classmethod
    def filter_queryset(cls, queryset, perm):
        return queryset.filter(owner=perm.user)


@translate_model
class Event(Model):
    # general
    name = CharField(max_length=63)
    is_canceled = BooleanField(default=False)
    is_closed = BooleanField(default=False)
    is_archived = BooleanField(default=False)
    start = DateField()
    start_time = TimeField(blank=True, null=True)
    end = DateField()
    number_of_sub_events = PositiveIntegerField(default=1)
    location = ForeignKey(Location, on_delete=PROTECT, related_name='events')
    online_link = URLField(blank=True)

    group = ForeignKey(EventGroupCategory, on_delete=PROTECT, related_name='events')
    category = ForeignKey(EventCategory, on_delete=PROTECT, related_name='events')
    tags = ManyToManyField(EventTag, related_name='events')
    program = ForeignKey(EventProgramCategory, on_delete=PROTECT, related_name='events')
    intended_for = ForeignKey(EventIntendedForCategory, on_delete=PROTECT, related_name='events')

    administration_units = ManyToManyField(AdministrationUnit, related_name='events')
    main_organizer = ForeignKey(User, on_delete=PROTECT, related_name='events_where_was_as_main_organizer', null=True)
    other_organizers = ManyToManyField(User, related_name='events_where_was_organizer', blank=True)
    created_by = ForeignKey(User, on_delete=PROTECT, related_name='created_events', null=True)
    created_at = DateField(auto_now=True)

    is_attendance_list_required = BooleanField(default=False)
    internal_note = TextField(blank=True)

    _import_id = CharField(max_length=15, default='')
    duration = PositiveIntegerField()

    class Meta:
        ordering = '-start',
        app_label = 'bis'

    def __str__(self):
        return self.name

    def clean(self):
        if self.main_organizer:
            Qualification.validate_main_organizer(self, self.main_organizer)

    @update_roles('main_organizer')
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not cache.get('skip_validation'): self.clean()
        super().save(force_insert, force_update, using, update_fields)

    def is_volunteering(self):
        return self.category.slug == 'public__volunteering'

    def is_for_kids(self):
        return self.intended_for.slug in ['for_kids', 'for_parents_with_kids']

    @admin.display(description='Termín akce')
    def get_date(self):
        result = f'{self.end.day}. {self.end.month}. {self.end.year}'

        if self.start != self.end:
            result = '- ' + result
            if self.start.year != self.end.year:
                result = f"{self.start.year}. " + result
            if self.start.month != self.end.month:
                result = f"{self.start.month}. " + result
            if self.start.day != self.end.day:
                result = f"{self.start.day}. " + result

        # if time.hour != 0:
        #     result += f' {time.hour}:{time.minute:02d}'
        return result

    @classmethod
    def filter_queryset(cls, queryset, perm):
        if perm.source == 'backend':
            if perm.user.is_education_member:
                return queryset

            return queryset.filter(administration_units__board_members=perm.user)

        queries = [
            # ucast na akci
            Q(record__participants=perm.user),
            # prihlaseni na akci
            Q(registration__applications__user=perm.user),
        ]

        if perm.user.is_organizer:
            queries += [
                # kde jsem byl org
                Q(other_organizers=perm.user),
            ]

        if perm.user.is_board_member:
            queries += [
                # pod mym clankem
                Q(administration_units__board_members=perm.user)
            ]
        return filter_queryset_with_multiple_or_queries(queryset, queries)

    @permission_cache
    def has_edit_permission(self, user, ignore_archived=False):
        if self.is_archived and not ignore_archived: return False
        return user in self.other_organizers.all() or \
               self.administration_units.filter(board_members=user).exists()


@translate_model
class EventFinance(Model):
    event = OneToOneField(Event, related_name='finance', on_delete=CASCADE)

    bank_account_number = CharField(max_length=63, blank=True)

    grant_category = ForeignKey(GrantCategory, on_delete=PROTECT, related_name='events', null=True, blank=True)
    grant_amount = PositiveIntegerField(null=True, blank=True)
    total_event_cost = PositiveIntegerField(null=True, blank=True)
    budget = FileField(upload_to='budgets', blank=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'Finance k akci {self.event}'

    def has_edit_permission(self, user):
        return self.event.has_edit_permission(user)


@translate_model
class EventFinanceReceipt(Model):
    finance = ForeignKey(EventFinance, on_delete=CASCADE, related_name='receipts')
    receipt = FileField(upload_to='receipts')

    class Meta:
        ordering = 'id',

    def __str__(self):
        return basename(self.receipt.name)

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(finance__event__in=events)

    @permission_cache
    def has_edit_permission(self, user):
        return self.finance.has_edit_permission(user)


@translate_model
class EventPropagation(Model):
    event = OneToOneField(Event, related_name='propagation', on_delete=CASCADE)

    is_shown_on_web = BooleanField()

    minimum_age = PositiveIntegerField(null=True, blank=True)
    maximum_age = PositiveIntegerField(null=True, blank=True)
    cost = CharField(max_length=12)
    accommodation = CharField(max_length=255, blank=True)
    working_hours = PositiveSmallIntegerField(null=True, blank=True)
    working_days = PositiveSmallIntegerField(null=True, blank=True)
    diets = ManyToManyField(DietCategory, related_name='events', blank=True)
    organizers = CharField(max_length=255)
    web_url = URLField(blank=True)
    _contact_url = URLField(blank=True)

    invitation_text_introduction = HTMLField()
    invitation_text_practical_information = HTMLField()
    invitation_text_work_description = HTMLField(blank=True)
    invitation_text_about_us = HTMLField(blank=True)
    # propagation_images as Model below

    contact_name = CharField(max_length=63)
    contact_phone = PhoneNumberField(blank=True)
    contact_email = EmailField(blank=True)

    def clean(self):
        if self.event.is_volunteering():
            if not self.invitation_text_work_description:
                raise ValidationError('Popis dobrovolnické pomoci je povinný pro dobrovolnické akce')

            if not self.working_hours:
                raise ValidationError('Počet odpracovaných hodin (denně pro vícedenní akce) je povinný pro '
                                      'dobrovolnické akce')

            if not self.working_days and self.event.group.slug == 'camp':
                raise ValidationError('Počet pracovních dní je povinný pro dobrovolnické tábory')

        if not self.contact_phone and not self.contact_email:
            raise ValidationError("Kontaktní telefon či kontaktní e-mail musí být vyplněn")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not cache.get('skip_validation'): self.clean()
        self.contact_email = self.contact_email.lower()
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'Propagace k akci {self.event}'

    def has_edit_permission(self, user):
        return self.event.has_edit_permission(user)


@translate_model
class VIPEventPropagation(Model):
    event = OneToOneField(Event, related_name='vip_propagation', on_delete=CASCADE, blank=True, null=True)

    goals_of_event = TextField(blank=True)
    program = TextField(blank=True)
    short_invitation_text = TextField(max_length=200, blank=True)

    rover_propagation = BooleanField(default=False)


@translate_model
class EventRegistration(Model):
    event = OneToOneField(Event, related_name='registration', on_delete=CASCADE)

    is_registration_required = BooleanField(default=True)
    alternative_registration_link = URLField(blank=True)
    is_event_full = BooleanField(default=False)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'Přihlášení k akci {self.event}'

    def has_edit_permission(self, user):
        return self.event.has_edit_permission(user)


@translate_model
class EventRecord(Model):
    event = OneToOneField(Event, related_name='record', on_delete=CASCADE)

    total_hours_worked = PositiveIntegerField(null=True, blank=True)
    comment_on_work_done = TextField(blank=True)
    participants = ManyToManyField(User, 'participated_in_events', blank=True)
    number_of_participants = PositiveIntegerField(null=True, blank=True)
    number_of_participants_under_26 = PositiveIntegerField(null=True, blank=True)

    note = TextField(blank=True)

    class Meta:
        ordering = '-event__start',

    def __str__(self):
        return f'Záznam z akce {self.event}'

    def has_edit_permission(self, user):
        return self.event.has_edit_permission(user)

    def get_participants_count(self):
        return self.number_of_participants or len(self.get_all_participants())

    def get_young_participants_count(self):
        under_26 = len([p for p in self.get_all_participants() if
                        p.birthday and relativedelta(self.event.start, p.birthday).years <= 26])
        return self.number_of_participants_under_26 or under_26

    def get_young_percentage(self):
        participants_count = self.get_participants_count()
        if not participants_count: return '0%'
        return f"{int(self.get_young_participants_count() / participants_count * 100)}%"

    def get_all_participants(self):
        all_participants = self.participants.all().union(self.event.other_organizers.all())
        return User.objects.filter(id__in=all_participants.values_list('id'))


@translate_model
class EventContact(BaseContact):
    record = ForeignKey(EventRecord, on_delete=CASCADE, related_name='contacts')

    def has_edit_permission(self, user):
        return self.record.has_edit_permission(user)

    def clean(self):
        pass



@translate_model
class EventPropagationImage(Model):
    propagation = ForeignKey(EventPropagation, on_delete=CASCADE, related_name='images')
    order = PositiveIntegerField()
    image = ThumbnailImageField(upload_to='event_propagation_images', max_length=200)

    @admin.display(description='Náhled')
    def image_tag(self):
        return mark_safe(f'<img src="{self.image.urls["small"]}" />')

    class Meta:
        ordering = 'order',

    def __str__(self):
        return basename(self.image.name)

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(propagation__event__in=events)

    def has_edit_permission(self, user):
        return self.propagation.has_edit_permission(user)


@translate_model
class EventAttendanceListPage(Model):
    record = ForeignKey(EventRecord, on_delete=CASCADE, related_name='attendance_list_pages')
    page = ImageField(upload_to='attendance_list_pages', null=True, blank=True)

    class Meta:
        ordering = 'id',

    def __str__(self):
        return basename(self.page.name)

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(record__event__in=events)

    def has_edit_permission(self, user):
        return self.record.has_edit_permission(user)

@translate_model
class EventPhoto(Model):
    record = ForeignKey(EventRecord, on_delete=CASCADE, related_name='photos')
    photo = ThumbnailImageField(upload_to='event_photos')

    @admin.display(description='Náhled')
    def photo_tag(self):
        return mark_safe(f'<img style="max-height: 10rem; max-width: 20rem" src="{self.photo.url}" />')

    class Meta:
        ordering = 'id',

    def __str__(self):
        return basename(self.photo.name)

    @classmethod
    def filter_queryset(cls, queryset, perm):
        events = Event.filter_queryset(Event.objects.all(), perm)
        return queryset.filter(record__event__in=events)

    def has_edit_permission(self, user):
        return self.record.has_edit_permission(user)
