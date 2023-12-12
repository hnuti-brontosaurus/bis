from administration_units.models import AdministrationSubUnit, AdministrationUnit
from bis.models import Location, LocationPhoto, User
from categories.serializers import (
    AdministrationUnitCategorySerializer,
    DietCategorySerializer,
    EventCategorySerializer,
    EventGroupCategorySerializer,
    EventIntendedForCategorySerializer,
    EventProgramCategorySerializer,
    EventTagSerializer,
    LocationAccessibilityCategorySerializer,
    LocationProgramCategorySerializer,
    OpportunityCategorySerializer,
)
from event.models import (
    Event,
    EventPropagation,
    EventPropagationImage,
    EventRegistration,
)
from opportunities.models import Opportunity
from phonenumber_field.serializerfields import PhoneNumberField
from questionnaire.models import Question, Questionnaire
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import SlugRelatedField, StringRelatedField
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    name = SerializerMethodField()
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = "id", "name", "email", "phone"

    def get_name(self, instance) -> str:
        return instance.get_name()


class EventPropagationImageSerializer(ModelSerializer):
    class Meta:
        model = EventPropagationImage
        fields = ("image",)


class EventPropagationSerializer(ModelSerializer):
    diets = DietCategorySerializer(many=True)
    images = EventPropagationImageSerializer(many=True)
    contact_name = SerializerMethodField()
    contact_phone = SerializerMethodField()
    contact_email = SerializerMethodField()

    class Meta:
        model = EventPropagation
        fields = (
            "minimum_age",
            "maximum_age",
            "cost",
            "accommodation",
            "working_days",
            "working_hours",
            "diets",
            "organizers",
            "web_url",
            "invitation_text_introduction",
            "invitation_text_practical_information",
            "invitation_text_work_description",
            "invitation_text_about_us",
            "contact_name",
            "contact_phone",
            "contact_email",
            "images",
        )

    def get_contact_name(self, instance) -> str:
        return instance.contact_name

    def get_contact_phone(self, instance) -> str:
        return str(instance.contact_phone)

    def get_contact_email(self, instance) -> str:
        return instance.contact_email


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = "id", "question", "data", "is_required", "order"


class QuestionnaireSerializer(ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = "introduction", "after_submit_text", "questions"


class EventRegistrationSerializer(ModelSerializer):
    questionnaire = QuestionnaireSerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = (
            "is_registration_required",
            "is_event_full",
            "questionnaire",
            "alternative_registration_link",
        )


class LocationPhotoSerializer(ModelSerializer):
    class Meta:
        model = LocationPhoto
        fields = ("photo",)


class LocationSerializer(ModelSerializer):
    patron = UserSerializer()
    program = LocationProgramCategorySerializer()
    accessibility_from_prague = LocationAccessibilityCategorySerializer()
    accessibility_from_brno = LocationAccessibilityCategorySerializer()
    region = StringRelatedField()
    photos = LocationPhotoSerializer(many=True)

    class Meta:
        model = Location
        fields = (
            "name",
            "description",
            "patron",
            "program",
            "accessibility_from_prague",
            "accessibility_from_brno",
            "volunteering_work",
            "volunteering_work_done",
            "volunteering_work_goals",
            "options_around",
            "facilities",
            "web",
            "address",
            "gps_location",
            "region",
            "photos",
        )


class EventSerializer(ModelSerializer):
    propagation = EventPropagationSerializer(read_only=True)
    registration = EventRegistrationSerializer(read_only=True)

    location = LocationSerializer()
    group = EventGroupCategorySerializer()
    category = EventCategorySerializer()
    tags = EventTagSerializer(many=True)
    program = EventProgramCategorySerializer()
    intended_for = EventIntendedForCategorySerializer()
    administration_units = SlugRelatedField(
        slug_field="abbreviation", read_only=True, many=True
    )

    class Meta:
        model = Event

        fields = (
            "id",
            "name",
            "start",
            "start_time",
            "end",
            "duration",
            "location",
            "group",
            "category",
            "tags",
            "program",
            "intended_for",
            "administration_units",
            "propagation",
            "registration",
        )


class OpportunitySerializer(ModelSerializer):
    category = OpportunityCategorySerializer()
    location = LocationSerializer()
    contact_name = SerializerMethodField()
    contact_phone = SerializerMethodField()
    contact_email = SerializerMethodField()

    class Meta:
        model = Opportunity

        fields = (
            "id",
            "category",
            "name",
            "start",
            "end",
            "on_web_start",
            "on_web_end",
            "location",
            "introduction",
            "description",
            "location_benefits",
            "personal_benefits",
            "requirements",
            "contact_name",
            "contact_phone",
            "contact_email",
            "image",
        )

    def get_contact_name(self, instance) -> str:
        return (
            instance.contact_name
            or instance.contact_person
            and instance.contact_person.get_name()
        )

    def get_contact_phone(self, instance) -> str:
        return (
            str(instance.contact_phone)
            or instance.contact_person
            and str(instance.contact_person.phone)
        )

    def get_contact_email(self, instance) -> str:
        return (
            instance.contact_email
            or instance.contact_person
            and instance.contact_person.email
        )


class AdministrationSubUnitSerializer(ModelSerializer):
    phone = PhoneNumberField()
    main_leader = UserSerializer()
    sub_leaders = UserSerializer(many=True)
    address = StringRelatedField()

    class Meta:
        model = AdministrationSubUnit

        fields = (
            "id",
            "name",
            "description",
            "is_for_kids",
            "is_active",
            "phone",
            "email",
            "www",
            "facebook",
            "instagram",
            "address",
            "gps_location",
            "main_leader",
            "sub_leaders",
        )


class AdministrationUnitSerializer(ModelSerializer):
    phone = PhoneNumberField()
    category = AdministrationUnitCategorySerializer()
    chairman = UserSerializer()
    vice_chairman = UserSerializer()
    manager = UserSerializer()
    board_members = UserSerializer(many=True)
    address = StringRelatedField()
    contact_address = StringRelatedField()
    sub_units = AdministrationSubUnitSerializer(many=True)

    class Meta:
        model = AdministrationUnit

        fields = (
            "id",
            "name",
            "abbreviation",
            "description",
            "image",
            "is_for_kids",
            "phone",
            "email",
            "www",
            "facebook",
            "instagram",
            "ic",
            "address",
            "contact_address",
            "bank_account_number",
            "existed_since",
            "existed_till",
            "gps_location",
            "category",
            "chairman",
            "vice_chairman",
            "manager",
            "board_members",
            "sub_units",
        )
