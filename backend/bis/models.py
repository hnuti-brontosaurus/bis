import datetime
from functools import cached_property
from os.path import basename
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.gis.db.models import *
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField

from administration_units.models import AdministrationUnit, BrontosaurusMovement
from bis.admin_helpers import get_admin_edit_url
from bis.helpers import permission_cache, paused_validation, filter_queryset_with_multiple_or_queries
from categories.models import QualificationCategory, MembershipCategory, LocationProgramCategory, \
    LocationAccessibilityCategory, \
    RoleCategory, HealthInsuranceCompany, PronounCategory
from common.abstract_models import BaseContact, BaseAddress
from common.thumbnails import ThumbnailImageField
from translation.translate import translate_model


@translate_model
class Location(Model):
    name = CharField(max_length=63)
    description = TextField(blank=True)
    address = CharField(max_length=255, blank=True)
    gps_location = PointField(null=True)

    is_fully_specified = BooleanField(default=False)
    for_beginners = BooleanField(default=False)
    is_full = BooleanField(default=False)
    is_unexplored = BooleanField(default=False)

    program = ForeignKey(LocationProgramCategory, on_delete=PROTECT, null=True, blank=True)
    accessibility_from_prague = ForeignKey(LocationAccessibilityCategory, on_delete=PROTECT, related_name='+',
                                           null=True, blank=True)
    accessibility_from_brno = ForeignKey(LocationAccessibilityCategory, on_delete=PROTECT, related_name='+', null=True,
                                         blank=True)

    volunteering_work = TextField(blank=True)
    volunteering_work_done = TextField(blank=True)
    volunteering_work_goals = TextField(blank=True)
    options_around = TextField(blank=True)
    facilities = TextField(blank=True)

    web = URLField(blank=True)
    region = ForeignKey('regions.Region', related_name='locations', on_delete=PROTECT, null=True, editable=False)

    _import_id = CharField(max_length=15, default='')

    class Meta:
        ordering = 'name',

    def __str__(self):
        return self.name

    @permission_cache
    def has_edit_permission(self, user):
        return not user.is_member_only

    @admin.display(description='Akce na lokalitě')
    def get_events(self):
        return mark_safe(', '.join(get_admin_edit_url(e) for e in self.events.all()))

    @classmethod
    @transaction.atomic
    def merge(cls, queryset, to_last):
        with paused_validation():
            queryset = list(queryset.order_by("name"))
            assert len(queryset) > 1, "Je třeba vybrat dvě a více lokalit"
            if to_last:
                first, rest = queryset[-1], queryset[:-1]
            else:
                first, rest = queryset[0], queryset[1:]
            for other in rest:
                for field in first._meta.fields:
                    if field.name in ['id', '_import_id']:
                        continue

                    elif field.name in ['name', 'description', 'address', 'gps_location', 'is_fully_specified',
                                        'for_beginners', 'is_full', 'is_unexplored', 'program', 'accessibility_from_prague',
                                        'accessibility_from_brno', 'volunteering_work', 'volunteering_work_done',
                                        'volunteering_work_goals', 'options_around', 'facilities', 'web', 'region']:
                        if not getattr(first, field.name) and getattr(other, field.name):
                            setattr(first, field.name, getattr(other, field.name))

                    else:
                        raise RuntimeError(f'field {field.name} not checked, database was updated, merge is outdated')

                for relation in first._meta.related_objects:
                    if relation.name in ['contact_person', 'patron']:
                        print(relation.name, hasattr(first, relation.name), hasattr(other, relation.name))
                        if not hasattr(first, relation.name) and hasattr(other, relation.name):
                            obj = getattr(other, relation.name)
                            obj.location = first
                            obj.save()

                    elif isinstance(relation, ManyToOneRel) or isinstance(relation, OneToOneRel):
                        for obj in relation.field.model.objects.filter(**{relation.field.name: other}):
                            setattr(obj, relation.field.name, first)
                            obj.save()

                    elif isinstance(relation, ManyToManyRel):
                        for obj in relation.field.model.objects.filter(**{relation.field.name: other}):
                            getattr(obj, relation.field.name).add(first)
                            getattr(obj, relation.field.name).remove(other)

                    else:
                        raise RuntimeError('should not happen :)')

            first.save()
            [item.delete() for item in rest]

        return first


@translate_model
class LocationPhoto(Model):
    location = ForeignKey(Location, on_delete=CASCADE, related_name='photos')
    photo = ThumbnailImageField(upload_to='location_photos')

    @admin.display(description='Náhled')
    def photo_tag(self):
        return mark_safe(f'<img style="max-height: 10rem; max-width: 20rem" src="{self.photo.url}" />')

    class Meta:
        ordering = 'id',

    def __str__(self):
        return basename(self.photo.name)

    @permission_cache
    def has_edit_permission(self, user):
        return self.location.has_edit_permission(user)


@translate_model
class LocationContactPerson(BaseContact):
    location = OneToOneField(Location, on_delete=CASCADE, related_name='contact_person')

    @permission_cache
    def has_edit_permission(self, user):
        return self.location.has_edit_permission(user)


@translate_model
class LocationPatron(BaseContact):
    location = OneToOneField(Location, on_delete=CASCADE, related_name='patron')

    @permission_cache
    def has_edit_permission(self, user):
        return self.location.has_edit_permission(user)


@translate_model
class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'

    id = UUIDField(primary_key=True, verbose_name='ID', default=uuid4, auto_created=True, editable=False)
    _search_id = UUIDField(default=uuid4, auto_created=True, editable=False)

    first_name = CharField(max_length=63)
    last_name = CharField(max_length=63)
    nickname = CharField(max_length=63, blank=True)
    birth_name = CharField(max_length=63, blank=True)
    phone = PhoneNumberField(blank=True)
    email = EmailField(unique=True, blank=True, null=True)
    birthday = DateField(null=True)

    subscribed_to_newsletter = BooleanField(default=True)

    health_insurance_company = ForeignKey(HealthInsuranceCompany, related_name='users', on_delete=PROTECT, null=True,
                                          blank=True)
    health_issues = TextField(blank=True)
    pronoun = ForeignKey(PronounCategory, on_delete=PROTECT, null=True, blank=True, related_name='users')

    is_active = BooleanField(default=True)
    date_joined = DateField(default=datetime.date.today)
    internal_note = TextField(blank=True)

    _import_id = CharField(max_length=255, default='')
    _str = CharField(max_length=255)
    roles = ManyToManyField(RoleCategory, related_name='users')
    vokativ = CharField(max_length=63, blank=True)

    objects = UserManager()

    @cached_property
    def is_director(self):
        return self.roles.filter(slug='director').exists()

    @cached_property
    def is_admin(self):
        return self.roles.filter(slug='admin').exists()

    @cached_property
    def is_office_worker(self):
        return self.roles.filter(slug='office_worker').exists()

    @cached_property
    def is_auditor(self):
        return self.roles.filter(slug='auditor').exists()

    @cached_property
    def is_executive(self):
        return self.roles.filter(slug='executive').exists()

    @cached_property
    def is_education_member(self):
        return self.roles.filter(slug='education_member').exists()

    @cached_property
    def is_board_member(self):
        return self.roles.filter(slug='board_member').exists()

    @cached_property
    def is_chairman(self):
        return self.roles.filter(slug='chairman').exists()

    @cached_property
    def is_vice_chairman(self):
        return self.roles.filter(slug='vice_chairman').exists()

    @cached_property
    def is_manager(self):
        return self.roles.filter(slug='manager').exists()

    @cached_property
    def is_main_organizer(self):
        return self.roles.filter(slug='main_organizer').exists()

    @cached_property
    def is_organizer(self):
        return self.roles.filter(slug='organizer').exists()

    @cached_property
    def is_qualified_organizer(self):
        return self.roles.filter(slug='qualified_organizer').exists()

    @cached_property
    def is_member_only(self):
        return not self.roles.exclude(slug='any').exists()

    @cached_property
    def can_see_all(self):
        return self.is_superuser or self.is_office_worker or self.is_auditor \
            or self.is_executive

    @cached_property
    def is_staff(self):
        return self.is_superuser or self.is_office_worker or self.is_auditor \
            or self.is_executive or self.is_education_member or self.is_board_member

    @cached_property
    def is_superuser(self):
        return self.is_director or self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        if self.can_see_all or self.is_board_member:
            return True

        if self.is_education_member:
            return app_label in ['categories', 'bis', 'regions', 'other']

        return False

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def age(self):
        if self.birthday:
            return relativedelta(now().date(), self.birthday).years

    class Meta:
        ordering = 'last_name',
        unique_together = 'first_name', 'last_name', 'birthday'

    def __str__(self):
        return self._str

    @classmethod
    def get(cls, *, email=None, first_name=None, last_name=None, birthday=None):
        if email:
            email = email.lower()
            return cls.objects.filter(all_emails__email=email).first()

        if first_name and last_name and birthday:
            return cls.objects.filter(first_name=first_name, last_name=last_name, birthday=birthday).first()

    def clean(self):
        super().clean()

        if self.email:
            self.email = self.email.lower()
            user_email = UserEmail.objects.filter(email=self.email).first()
            if user_email and user_email.user != self:
                raise ValidationError(f'Cannot set e-mail {self.email} for user {self}, another user with '
                                      f'this email already exists')

    def save(self, *args, **kwargs):
        self.email = self.email or None
        if not cache.get('skip_validation'): self.clean()
        super().save(*args, **kwargs)

    @transaction.atomic
    def merge_with(self, other):
        assert other != self
        with paused_validation():
            print(cache.get('skip_validation'))
            for field in self._meta.fields:
                if field.name in ['id', 'password', '_import_id', 'is_active', 'last_login', '_str', 'roles', 'email',
                                  '_search_id', 'vokativ']:
                    continue

                elif field.name in ['date_joined', ]:
                    if getattr(other, field.name) < getattr(self, field.name):
                        setattr(self, field.name, getattr(other, field.name))

                elif field.name in ['first_name', 'last_name', 'nickname', 'birth_name', 'phone',
                                    'birthday', 'close_person', 'health_insurance_company', 'health_issues', 'pronoun',
                                    'subscribed_to_newsletter', 'internal_note']:
                    if not getattr(self, field.name) and getattr(other, field.name):
                        setattr(self, field.name, getattr(other, field.name))

                else:
                    raise RuntimeError(f'field {field.name} not checked, database was updated, merge is outdated')

            for relation in self._meta.related_objects:
                if relation.name in ['auth_token']:
                    continue

                elif relation.name in ['address', 'contact_address']:
                    if not hasattr(self, relation.name) and hasattr(other, relation.name):
                        obj = getattr(other, relation.name)
                        obj.user = self
                        obj.save()

                elif relation.name == 'donor':
                    if hasattr(other, relation.name):
                        if not hasattr(self, relation.name):
                            obj = getattr(other, relation.name)
                            obj.user = self
                            obj.save()
                        else:
                            self.donor.merge_with(other.donor)

                elif relation.name == 'all_emails':
                    max_order = max([email.order for email in self.all_emails.all()] + [0])
                    for i, obj in enumerate(list(UserEmail.objects.filter(user=other))):
                        obj.delete()
                        UserEmail.objects.create(email=obj.email, user=self, order=max_order + i + 1)

                elif isinstance(relation, ManyToOneRel) or isinstance(relation, OneToOneRel):
                    for obj in relation.field.model.objects.filter(**{relation.field.name: other}):
                        setattr(obj, relation.field.name, self)
                        obj.save()

                elif isinstance(relation, ManyToManyRel):
                    for obj in relation.field.model.objects.filter(**{relation.field.name: other}):
                        getattr(obj, relation.field.name).add(self)
                        getattr(obj, relation.field.name).remove(other)

                else:
                    raise RuntimeError('should not happen :)')

            other.delete()
            self.save()

    @admin.display(description='Uživatel')
    def get_name(self):
        name = f'{self.first_name} {self.last_name}'.strip()
        if self.nickname:
            if name:
                name = f'{self.nickname} ({name})'
            else:
                name = self.nickname

        if not name.strip():
            return f"{self.email}"

        return name

    def get_short_name(self):  # for admin
        return self.get_name()

    @admin.display(description='E-mailové adresy')
    def get_all_emails(self):
        return mark_safe("<br>".join(e.email for e in self.all_emails.all()))

    @admin.display(description='E-mail')
    def get_email(self):
        if not self.email:
            return ''

        name, host = self.email.split('@')
        return mark_safe(f'{name}<br>@{host}')

    @admin.display(description='Aktivní kvalifikace')
    def get_qualifications(self):
        if (self.age or 0) < 15: return []
        return [q for q in self.qualifications.all() if q.valid_since <= timezone.now().date() <= q.valid_till]

    @admin.display(description='Aktivní členství')
    def get_memberships(self):
        return [m for m in self.memberships.all() if m.year == timezone.now().year]

    @admin.display(description='Zorganizované akce')
    def get_events_where_was_organizer(self):
        return mark_safe(', '.join(get_admin_edit_url(e) for e in self.events_where_was_organizer.all()))

    @admin.display(description='Akce, kde byl účastníkem')
    def get_participated_in_events(self):
        return mark_safe(', '.join(get_admin_edit_url(e.event) for e in self.participated_in_events.all()))

    @admin.display(description='Profil dárce (pokud existuje)')
    def get_donor(self):
        if not hasattr(self, 'donor'):
            return 'Neexistuje'
        return get_admin_edit_url(getattr(self, 'donor'))

    @classmethod
    def filter_queryset(cls, queryset, perm):
        if perm.user.is_education_member:
            return queryset

        queries = [Q(id=perm.user.id)]  # me

        if perm.source != 'backend':
            if perm.user.is_organizer:
                queries += [
                    # lidi kolem akci, kde perm.user byl organizer
                    Q(participated_in_events__event__other_organizers=perm.user),
                    Q(events_where_was_organizer__other_organizers=perm.user),
                    Q(applications__event_registration__event__other_organizers=perm.user),
                ]

        if perm.user.is_board_member:
            queries += [
                # lidi kolem akci od clanku kde perm.user je board member
                Q(participated_in_events__event__administration_units__board_members=perm.user),
                Q(events_where_was_organizer__administration_units__board_members=perm.user),
                Q(applications__event_registration__event__administration_units__board_members=perm.user),
                # clenove meho clanku
                Q(memberships__administration_unit__board_members=perm.user),
            ]
        return filter_queryset_with_multiple_or_queries(queryset, queries)

    @permission_cache
    def has_edit_permission(self, user):
        if self == user: return True
        events = []
        events += apps.get_model('bis', 'Event').objects.filter(registration__applications__user=self)
        events += self.participated_in_events.all()
        events += self.events_where_was_organizer.all()
        events += apps.get_model('bis', 'Event').objects.filter(administration_units__board_members=self)
        for event in events:
            if event.has_edit_permission(user):
                return True

    def update_roles(self):
        roles = ['any']

        brontosaurus_movement = BrontosaurusMovement.get()
        if self in [brontosaurus_movement.director, brontosaurus_movement.finance_director]:
            roles += ['director']
        if self in brontosaurus_movement.bis_administrators.all():
            roles += ['admin']
        if self in brontosaurus_movement.office_workers.all():
            roles += ['office_worker']
        if self in brontosaurus_movement.audit_committee.all():
            roles += ['auditor']
        if self in brontosaurus_movement.executive_committee.all():
            roles += ['executive']
        if self in brontosaurus_movement.education_members.all():
            roles += ['education_member']
        if self.chairman_of.exists():
            roles += ['chairman']
        if self.vice_chairman_of.exists():
            roles += ['vice_chairman']
        if self.manager_of.exists():
            roles += ['manager']
        if self.administration_units.exists():
            roles += ['board_member', 'organizer']
        if self.events_where_was_as_main_organizer.exists():
            roles += ['main_organizer']
        if self.events_where_was_organizer.exists():
            roles += ['organizer']
        if self.get_qualifications():
            roles += ['qualified_organizer', 'organizer']

        roles = [RoleCategory.objects.get(slug=role) for role in set(roles)]

        self.roles.set(roles)


@translate_model
class UserEmail(Model):
    user = ForeignKey(User, related_name='all_emails', on_delete=CASCADE)
    email = EmailField(unique=True)
    order = PositiveSmallIntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.email = self.email.lower()
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = 'order',

    def __str__(self):
        return self.email


@translate_model
class UserAddress(BaseAddress):
    user = OneToOneField(User, on_delete=CASCADE, related_name='address')


@translate_model
class UserContactAddress(BaseAddress):
    user = OneToOneField(User, on_delete=CASCADE, related_name='contact_address')


@translate_model
class UserClosePerson(BaseContact):
    user = OneToOneField(User, on_delete=CASCADE, related_name='close_person')


@translate_model
class EYCACard(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='eyca_card')
    photo = ThumbnailImageField(upload_to='eyca_photos')
    number = CharField(max_length=63)
    submitted_for_creation = BooleanField(default=False)
    sent_to_user = BooleanField(default=False)
    valid_till = DateField(blank=True)


@translate_model
class Membership(Model):
    user = ForeignKey(User, on_delete=PROTECT, related_name='memberships')
    category = ForeignKey(MembershipCategory, on_delete=PROTECT, related_name='memberships')
    administration_unit = ForeignKey(AdministrationUnit, on_delete=PROTECT, related_name='memberships')
    year = PositiveIntegerField()

    _import_id = CharField(max_length=15, default='')

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'Člen {self.administration_unit} {self.category}, {self.year}'


@translate_model
class Qualification(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name='qualifications')
    category = ForeignKey(QualificationCategory, on_delete=PROTECT, related_name='qualifications')
    valid_since = DateField()
    valid_till = DateField()
    approved_by = ForeignKey(User, on_delete=PROTECT, related_name='approved_qualifications')

    _import_id = CharField(max_length=15, default='')

    class Meta:
        ordering = 'id',

    def __str__(self):
        return f'{self.category} (od {self.valid_since} do {self.valid_till})'

    def clean(self):
        approved_with = [category.slug for category in self.category.can_be_approved_with.all()]
        if not (
                self.approved_by.is_staff or self.approved_by.is_superuser or
                Qualification.user_has_required_qualification(self.approved_by, approved_with)

        ):
            approved_with = " nebo ".join([str(c) for c in self.category.can_be_approved_with.all()])
            raise ValidationError(f'Kvalifikace typu {self.category} musí být schválena člověkem s kvalifikací '
                                  f'{approved_with}, kvalifikací nadřazenou nebo ústředím.')

    def save(self, *args, **kwargs):
        if not cache.get('skip_validation'): self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def user_has_required_qualification(cls, user, required_one_of):
        qualifications = user.get_qualifications()
        for qualification in qualifications:
            for slug in qualification.category.get_slugs():
                if slug in required_one_of:
                    return True

    @classmethod
    def validate_main_organizer(cls, event, main_organizer: User):
        age = main_organizer.age
        intended_for = event.intended_for.slug
        group = event.group.slug
        category = event.category.slug

        qualification_required_for_categories = {'internal__general_meeting', 'internal__section_meeting',
                                                 'public__volunteering', 'public__only_experiential',
                                                 'public__sports', 'public__educational__course',
                                                 'public__educational__ohb', 'public__other__for_public', }

        if category not in qualification_required_for_categories:
            return

        if not age:
            raise ValidationError('Není znám věk hlavního organizátora')

        if age < 18:
            raise ValidationError('Hlavní organizátor musí mít aspoň 18 let')

        required_one_of = set()

        if intended_for == 'for_kids':
            if group == 'camp' or category == 'internal__section_meeting':
                required_one_of = {'kids_leader'}
            else:
                required_one_of = {'kids_intern'}

        if intended_for == 'for_parents_with_kids':
            if group == 'camp':
                required_one_of = {'kids_leader', 'organizer'}
            if group == 'weekend_event':
                required_one_of = {'kids_intern', 'weekend_organizer'}

        if intended_for in {'for_all', 'for_young_and_adult', 'for_first_time_participant'}:
            if group == 'camp':
                required_one_of = {'organizer'}
            if group == 'weekend_event':
                required_one_of = {'weekend_organizer'}

        if category == 'public__educational__ohb':
            required_one_of = {'instructor', 'consultant_for_kids'}

        if required_one_of:
            if not cls.user_has_required_qualification(main_organizer, required_one_of):
                categories = [str(QualificationCategory.objects.get(slug=slug)) for slug in required_one_of]
                raise ValidationError(f'Hlavní organizátor {main_organizer} musí mít kvalifikaci '
                                      f'{" nebo ".join(categories)} nebo kvalifikací nadřazenou.')
