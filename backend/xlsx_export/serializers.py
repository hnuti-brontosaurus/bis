from rest_framework.fields import SerializerMethodField, ReadOnlyField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from bis.models import User, Location
from donations.models import Donor
from event.models import Event, EventFinance, EventPropagation, EventRegistration, EventRecord
from opportunities.models import OfferedHelp


class OfferedHelpExportSerializer(ModelSerializer):
    programs = StringRelatedField(many=True)
    organizer_roles = StringRelatedField(many=True)
    team_roles = StringRelatedField(many=True)

    class Meta:
        model = OfferedHelp
        fields = (
            'programs',
            'organizer_roles',
            'additional_organizer_role',
            'team_roles',
            'additional_team_role',
            'info',
        )


class UserExportSerializer(ModelSerializer):
    roles = StringRelatedField(label='Role', many=True)
    email = SerializerMethodField(label='Email')
    get_name = ReadOnlyField(label='Celé jméno')
    age = ReadOnlyField(label='Věk')
    address = StringRelatedField(label='Adresa')
    contact_address = StringRelatedField(label='Kontaktí adresa')
    offers = OfferedHelpExportSerializer()
    sex = StringRelatedField(label='Pohlaví')

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            'address', 'contact_address',
            'offers',
            'health_insurance_company',
            'sex',
        ).prefetch_related(
            'emails', 'roles',
            'offers__programs',
            'offers__organizer_roles',
            'offers__team_roles',
        )

    class Meta:
        model = User

        fields = (
            'id',
            'get_name',
            'first_name',
            'last_name',
            'nickname',
            'email',
            'phone',
            'birthday',
            'age',
            'health_insurance_company',
            'health_issues',
            'is_active',
            'date_joined',
            'roles',
            'address',
            'contact_address',
            'offers',
            'sex',
        )

    def get_email(self, instance):
        return instance.emails.first() or ''


class DonorExportSerializer(ModelSerializer):
    user = UserExportSerializer()
    variable_symbols = StringRelatedField(many=True)
    regional_center_support = StringRelatedField()
    basic_section_support = StringRelatedField()

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            'user__address', 'user__contact_address',
            'regional_center_support',
            'basic_section_support',
            'user__offers',
            'user__health_insurance_company',
            'user__sex',
        ).prefetch_related(
            'user__emails', 'user__roles',
            'variable_symbols',
            'user__offers__programs',
            'user__offers__organizer_roles',
            'user__offers__team_roles',
        )

    class Meta:
        model = Donor
        fields = (
            'user',
            'subscribed_to_newsletter',
            'is_public',
            'has_recurrent_donation',
            'date_joined',
            'regional_center_support',
            'basic_section_support',
            'variable_symbols',
        )


class LocationExportSerializer(ModelSerializer):
    program = StringRelatedField(label='Program lokality')
    accessibility_from_prague = StringRelatedField(label='Dostupnost z Prahy')
    accessibility_from_brno = StringRelatedField(label='Dostupnost z Brna')
    region = StringRelatedField(label='Kraj')

    class Meta:
        model = Location
        fields = (
            'name',
            'for_beginners',
            'is_full',
            'is_unexplored',
            'program',
            'accessibility_from_prague',
            'accessibility_from_brno',
            'region',
        )


class FinanceExportSerializer(ModelSerializer):
    grant_category = StringRelatedField(label='Typ grantu')

    class Meta:
        model = EventFinance
        fields = (
            'bank_account_number',
            'grant_category',
            'grant_amount',
            'total_event_cost',
        )


class PropagationExportSerializer(ModelSerializer):
    intended_for = StringRelatedField(label='Pro koho')
    diets = StringRelatedField(label='Diety', many=True)

    class Meta:
        model = EventPropagation
        fields = (
            'is_shown_on_web',
            'minimum_age',
            'maximum_age',
            'cost',
            'discounted_cost',
            'intended_for',
            'diets',
        )


class RegistrationExportSerializer(ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = (
            'is_registration_required',
            'is_event_full',
        )


class RecordExportSerializer(ModelSerializer):
    get_participants_count = ReadOnlyField(label='Počet účastníků')
    get_young_percentage = ReadOnlyField(label='% do 26')

    class Meta:
        model = EventRecord
        fields = (
            'total_hours_worked',
            'working_hours',
            'working_days',
            'comment_on_work_done',
            'get_participants_count',
            'get_young_percentage',
        )


class EventExportSerializer(ModelSerializer):
    category = StringRelatedField(label='Typ akce')
    program = StringRelatedField(label='Program')
    administration_units = StringRelatedField(label='Organizováno', many=True)
    main_organizer = StringRelatedField(label='Hlavní org')
    other_organizers = StringRelatedField(label='Orgové', many=True)
    is_volunteering = ReadOnlyField(label='S dobrovolnickou prací')
    get_date = ReadOnlyField(label='Hezké datum')

    location = LocationExportSerializer()
    finance = FinanceExportSerializer()
    propagation = PropagationExportSerializer()
    registration = RegistrationExportSerializer()
    record = RecordExportSerializer()

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            'location',
            'location__program',
            'location__accessibility_from_prague',
            'location__accessibility_from_brno',
            'location__region',
            'category',
            'program',
            'main_organizer',
            'finance',
            'finance__grant_category',
            'propagation',
            'propagation__intended_for',
            'registration',
            'record',
        ).prefetch_related(
            'administration_units',
            'other_organizers',
            'propagation__diets'
        )

    class Meta:
        model = Event

        fields = (
            'name',
            'is_canceled',
            'start',
            'end',
            'get_date',
            'duration',
            'number_of_sub_events',
            'location',
            'online_link',
            'category',
            'is_volunteering',
            'program',
            'administration_units',
            'main_organizer',
            'other_organizers',
            'is_attendance_list_required',
            'is_internal',
            'internal_note',
            'finance',
            'propagation',
            'registration',
            'record',
        )
