from administration_units.models import AdministrationUnit
from bis.models import Location, User, UserClosePerson
from donations.models import Donation, Donor
from event.models import (
    Event,
    EventFinance,
    EventPropagation,
    EventRecord,
    EventRegistration,
)
from opportunities.models import OfferedHelp
from questionnaire.models import EventApplication, Question
from rest_framework.fields import ReadOnlyField, SerializerMethodField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer


class OfferedHelpExportSerializer(ModelSerializer):
    programs = StringRelatedField(many=True)
    organizer_roles = StringRelatedField(many=True)
    team_roles = StringRelatedField(many=True)

    class Meta:
        model = OfferedHelp
        fields = (
            "programs",
            "organizer_roles",
            "additional_organizer_role",
            "team_roles",
            "additional_team_role",
            "info",
        )


class ClosePersonExportSerializer(ModelSerializer):
    class Meta:
        model = UserClosePerson
        fields = (
            "first_name",
            "last_name",
            "phone",
            "email",
        )


class UserExportSerializer(ModelSerializer):
    roles = StringRelatedField(label="Role", many=True)
    get_name = ReadOnlyField(label="Celé jméno")
    age = ReadOnlyField(label="Věk")
    address = StringRelatedField(label="Adresa")
    contact_address = StringRelatedField(label="Kontaktí adresa")
    offers = OfferedHelpExportSerializer()
    pronoun = StringRelatedField(label="Oslovení")
    all_emails = StringRelatedField(label="Všechny e-maily", many=True)
    qualifications = StringRelatedField(label="Kvalifikace", many=True)
    memberships = StringRelatedField(label="Členství", many=True)
    eyca_card = StringRelatedField(label="EYCA")
    close_person = ClosePersonExportSerializer()

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            "address",
            "contact_address",
            "offers",
            "health_insurance_company",
            "pronoun",
            "eyca_card",
        ).prefetch_related(
            "roles",
            "all_emails",
            "qualifications",
            "memberships",
            "offers__programs",
            "offers__organizer_roles",
            "offers__team_roles",
        )

    class Meta:
        model = User

        fields = (
            "id",
            "first_name",
            "last_name",
            "get_name",
            "nickname",
            "birthday",
            "address",
            "contact_address",
            "phone",
            "email",
            "all_emails",
            "qualifications",
            "memberships",
            "age",
            "health_insurance_company",
            "health_issues",
            "date_joined",
            "roles",
            "subscribed_to_newsletter",
            "eyca_card",
            "pronoun",
            "close_person",
            "offers",
        )


class DonorExportSerializer(ModelSerializer):
    user = UserExportSerializer()
    variable_symbols = StringRelatedField(many=True)
    regional_center_support = StringRelatedField()
    basic_section_support = StringRelatedField()

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            "user__address",
            "user__contact_address",
            "regional_center_support",
            "basic_section_support",
            "user__offers",
            "user__health_insurance_company",
            "user__pronoun",
        ).prefetch_related(
            "user__roles",
            "variable_symbols",
            "user__offers__programs",
            "user__offers__organizer_roles",
            "user__offers__team_roles",
        )

    class Meta:
        model = Donor
        fields = (
            "user",
            "subscribed_to_newsletter",
            "is_public",
            "has_recurrent_donation",
            "date_joined",
            "regional_center_support",
            "basic_section_support",
            "variable_symbols",
        )


class LocationExportSerializer(ModelSerializer):
    region = StringRelatedField(label="Kraj")

    class Meta:
        model = Location
        fields = (
            "is_traditional",
            "region",
        )


class FinanceExportSerializer(ModelSerializer):
    grant_category = StringRelatedField(label="Typ grantu")

    class Meta:
        model = EventFinance
        fields = (
            "bank_account_number",
            "grant_category",
            "grant_amount",
            "total_event_cost",
        )


class PropagationExportSerializer(ModelSerializer):
    diets = StringRelatedField(label="Možnosti stravování", many=True)

    class Meta:
        model = EventPropagation
        fields = (
            "is_shown_on_web",
            "minimum_age",
            "maximum_age",
            "cost",
            "diets",
            "working_hours",
            "working_days",
        )


class RegistrationExportSerializer(ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = (
            "is_registration_required",
            "alternative_registration_link",
            "is_event_full",
        )


class RecordExportSerializer(ModelSerializer):
    get_participants_count = ReadOnlyField(label="Počet účastníků")
    get_young_participants_count = ReadOnlyField(label="Z toho účastníků do 26 let")
    get_young_percentage = ReadOnlyField(label="% účastníků do 26 let")

    class Meta:
        model = EventRecord
        fields = (
            "get_participants_count",
            "get_young_participants_count",
            "get_young_percentage",
            "total_hours_worked",
            "comment_on_work_done",
            "note",
        )


class EventExportSerializer(ModelSerializer):
    group = StringRelatedField(label="Druh akce")
    category = StringRelatedField(label="Typ akce")
    tags = StringRelatedField(label="Štítky akce", many=True)
    program = StringRelatedField(label="Program")
    intended_for = StringRelatedField(label="Pro koho")
    administration_units = StringRelatedField(label="Organizováno", many=True)
    main_organizer = StringRelatedField(label="Hlavní org")
    other_organizers = StringRelatedField(label="Orgové", many=True)
    is_volunteering = ReadOnlyField(label="S dobrovolnickou prací")
    get_date = ReadOnlyField(label="Datum konání")

    location = LocationExportSerializer()
    finance = FinanceExportSerializer()
    propagation = PropagationExportSerializer()
    registration = RegistrationExportSerializer()
    record = RecordExportSerializer()
    location_name = SerializerMethodField(label="Místo konání")

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            "location",
            "location__program",
            "location__accessibility_from_prague",
            "location__accessibility_from_brno",
            "location__region",
            "category",
            "program",
            "main_organizer",
            "finance",
            "finance__grant_category",
            "propagation",
            "intended_for",
            "registration",
            "record",
        ).prefetch_related(
            "administration_units",
            "other_organizers",
            "propagation__diets",
            "tags",
        )

    class Meta:
        model = Event

        fields = (
            "name",
            "start",
            "start_time",
            "end",
            "location_name",
            "record",
            "group",
            "category",
            "tags",
            "program",
            "location",
            "is_canceled",
            "is_closed",
            "is_archived",
            "get_date",
            "duration",
            "number_of_sub_events",
            "online_link",
            "is_volunteering",
            "intended_for",
            "administration_units",
            "main_organizer",
            "other_organizers",
            "is_attendance_list_required",
            "internal_note",
            "finance",
            "propagation",
            "registration",
        )

    def get_location_name(self, instance):
        return instance.location.name


class DonationExportSerializer(ModelSerializer):
    donor = DonorExportSerializer()
    donation_source = StringRelatedField()

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            "donation_source",
            "donor__user__address",
            "donor__user__contact_address",
            "donor__regional_center_support",
            "donor__basic_section_support",
            "donor__user__offers",
            "donor__user__health_insurance_company",
            "donor__user__pronoun",
        ).prefetch_related(
            "donor__user__roles",
            "donor__variable_symbols",
            "donor__user__offers__programs",
            "donor__user__offers__organizer_roles",
            "donor__user__offers__team_roles",
        )

    class Meta:
        model = Donation
        fields = (
            "donated_at",
            "amount",
            "donation_source",
            "info",
            "donor",
        )


class AdministrationUnitExportSerializer(ModelSerializer):
    category = StringRelatedField()
    chairman = StringRelatedField()
    vice_chairman = StringRelatedField()
    manager = StringRelatedField()
    address = StringRelatedField(label="Adresa")
    contact_address = StringRelatedField(label="Kontaktí adresa")

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            "category",
            "chairman",
            "vice_chairman",
            "manager",
            "address",
            "contact_address",
        )

    class Meta:
        model = AdministrationUnit
        fields = (
            "id",
            "name",
            "abbreviation",
            "description",
            "is_for_kids",
            "phone",
            "email",
            "www",
            "facebook",
            "instagram",
            "ic",
            "bank_account_number",
            "data_box",
            "custom_statues",
            "gps_location",
            "existed_since",
            "existed_till",
            "category",
            "address",
            "contact_address",
            "chairman",
            "vice_chairman",
            "manager",
        )


class EventApplicationClosePersonExportSerializer(ModelSerializer):
    class Meta:
        model = UserClosePerson
        fields = (
            "first_name",
            "last_name",
            "phone",
            "email",
        )


class EventApplicationExportSerializer(ModelSerializer):
    close_person = EventApplicationClosePersonExportSerializer()
    address = StringRelatedField(label="Adresa")
    pronoun = StringRelatedField(label="Oslovení")
    state = SerializerMethodField(label="Stav přihlášky")

    @staticmethod
    def get_related(queryset):
        return queryset.select_related(
            "pronoun",
            "close_person",
            "address",
        ).prefetch_related(
            "answers",
        )

    class Meta:
        model = EventApplication
        fields = (
            "state",
            "is_child_application",
            "first_name",
            "last_name",
            "nickname",
            "phone",
            "email",
            "birthday",
            "health_issues",
            "pronoun",
            "created_at",
            "note",
            "close_person",
            "address",
        )

    def get_state(self, instance):
        return {k: v for k, v in instance.states}[instance.state]

    def to_representation(self, instance):
        result = super().to_representation(instance)
        for answer in instance.answers.all():
            result[str(answer.question.id)] = answer.answer
        return result

    def get_extra_fields(self, queryset):
        questions = Question.objects.filter(
            questionnaire__event_registration=queryset.first().event_registration
        )
        for question in questions:
            yield str(question.id), question.question
