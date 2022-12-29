from django.conf import settings
from django.contrib.gis.db.models import *
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from tinymce.models import HTMLField

from bis.models import User, Location
from categories.models import EventProgramCategory, TeamRoleCategory, OrganizerRoleCategory, OpportunityCategory
from common.thumbnails import ThumbnailImageField
from translation.translate import translate_model


@translate_model
class Opportunity(Model):
    category = ForeignKey(OpportunityCategory, on_delete=PROTECT, related_name='opportunities')
    name = CharField(max_length=63)
    start = DateField()
    end = DateField()
    on_web_start = DateField()
    on_web_end = DateField()
    location = ForeignKey(Location, on_delete=PROTECT, related_name='opportunities')

    introduction = HTMLField()
    description = HTMLField()
    location_benefits = HTMLField(blank=True)
    personal_benefits = HTMLField()
    requirements = HTMLField(blank=True)

    contact_person = ForeignKey(User, on_delete=PROTECT, related_name='opportunities')
    contact_name = CharField(max_length=63, blank=True)
    contact_phone = PhoneNumberField(blank=True)
    contact_email = EmailField(blank=True)
    image = ThumbnailImageField(upload_to='opportunity_images')

    def clean(self):
        if not (self.category.slug == 'collaboration' or self.location_benefits):
            raise ValidationError('Pokud kategorie spolupráce není Spolupráce, přínos pro lokalitu musí být vyplněn')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not settings.SKIP_VALIDATION: self.clean()
        self.contact_email = self.contact_email.lower()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    class Meta:
        ordering = 'id',

    @classmethod
    def filter_queryset(cls, queryset, user):
        visible_users = User.filter_queryset(User.objects.all(), user)
        return queryset.filter(contact_person__in=visible_users)

    def has_edit_permission(self, user):
        return self.contact_person == user

@translate_model
class OfferedHelp(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='offers')

    programs = ManyToManyField(EventProgramCategory, related_name='offered_help', blank=True, limit_choices_to=~Q(slug='none'))
    organizer_roles = ManyToManyField(OrganizerRoleCategory, related_name='offered_help', blank=True)
    additional_organizer_role = CharField(max_length=63, blank=True)
    team_roles = ManyToManyField(TeamRoleCategory, related_name='offered_help', blank=True)
    additional_team_role = CharField(max_length=63, blank=True)

    info = TextField(blank=True)

    def __str__(self):
        return f"Nabízená pomoc od {self.user}"

    class Meta:
        ordering = 'id',
