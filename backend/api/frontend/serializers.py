from datetime import date

from api.helpers import catch_related_object_does_not_exist
from bis.helpers import AgeStats, get_locked_year
from bis.models import (
    EYCACard,
    Location,
    LocationContactPerson,
    LocationPatron,
    Membership,
    Qualification,
    QualificationNote,
    User,
    UserAddress,
    UserClosePerson,
    UserContactAddress,
)
from categories.models import OpportunityPriority
from categories.serializers import (
    DietCategorySerializer,
    DonationSourceCategorySerializer,
    EventCategorySerializer,
    EventGroupCategorySerializer,
    EventIntendedForCategorySerializer,
    EventProgramCategorySerializer,
    EventTagSerializer,
    GrantCategorySerializer,
    HealthInsuranceCompanySerializer,
    LocationAccessibilityCategorySerializer,
    LocationProgramCategorySerializer,
    MembershipCategorySerializer,
    OpportunityCategorySerializer,
    OpportunityPrioritySerializer,
    OrganizerRoleCategorySerializer,
    PronounCategorySerializer,
    QualificationCategorySerializer,
    RoleCategorySerializer,
    TeamRoleCategorySerializer,
)
from dateutil.utils import today
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ManyToManyField
from donations.models import Donation, Donor
from event.models import (
    Event,
    EventAttendanceListPage,
    EventContact,
    EventDraft,
    EventFinance,
    EventFinanceReceipt,
    EventPhoto,
    EventPropagation,
    EventPropagationImage,
    EventRecord,
    EventRegistration,
    VIPEventPropagation,
)
from feedback.models import EventFeedback, FeedbackForm, Inquiry, Reply
from opportunities.models import OfferedHelp, Opportunity
from other.models import DashboardItem
from questionnaire.models import (
    Answer,
    EventApplication,
    EventApplicationAddress,
    EventApplicationClosePerson,
    Question,
    Questionnaire,
)
from regions.serializers import RegionSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (
    CharField,
    ChoiceField,
    DateField,
    IntegerField,
    SerializerMethodField,
    UUIDField,
)
from rest_framework.permissions import SAFE_METHODS
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ListSerializer
from rest_framework.serializers import ModelSerializer as DRFModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.utils import model_meta

from bis import emails


class ModelSerializer(DRFModelSerializer):
    @staticmethod
    def only_null_doesnt_mean_it_is_not_required(model_field, field_kwargs):
        if model_field.null and not model_field.blank:
            field_kwargs.pop("allow_null", None)
            if not model_field.has_default():
                field_kwargs.pop("required", None)

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )
        self.only_null_doesnt_mean_it_is_not_required(model_field, field_kwargs)
        return field_class, field_kwargs

    def build_relational_field(self, field_name, relation_info):
        field_class, field_kwargs = super().build_relational_field(
            field_name, relation_info
        )
        (
            model_field,
            related_model,
            to_many,
            to_field,
            has_through_model,
            reverse,
        ) = relation_info
        self.only_null_doesnt_mean_it_is_not_required(model_field, field_kwargs)
        return field_class, field_kwargs

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except DjangoValidationError as e:
            raise ValidationError(e.messages)

    @property
    def m2m_fields(self):
        info = model_meta.get_field_info(self.Meta.model)
        return [
            field_name
            for field_name, relation_info in info.relations.items()
            if (
                isinstance(relation_info.model_field, ManyToManyField)
                or isinstance(
                    getattr(
                        relation_info.related_model, relation_info.to_field or "", None
                    ),
                    ManyToManyField,
                )
            )
        ]

    @property
    def nested_serializers(self):
        result = {}
        for field_name, field in self.fields.items():
            if isinstance(field, ListSerializer):
                field = field.child
            if isinstance(field, ModelSerializer):
                result[field_name] = (
                    type(field),
                    self.Meta.model._meta.get_field(field_name).remote_field.name,
                )
        return result

    def get_excluded_fields(self, fields):
        return []

    def _exclude_fields(self, fields):
        for field in self.get_excluded_fields(fields):
            if field in fields:
                del fields[field]

        return fields

    def to_representation(self, instance):
        return self._exclude_fields(super().to_representation(instance))

    def to_internal_value(self, data):
        return self._exclude_fields(super().to_internal_value(data))

    @staticmethod
    def is_serializer_with_id(field):
        if isinstance(field, ListSerializer):
            field = field.child
        return isinstance(field, DRFModelSerializer) and "id" in field.get_fields()

    def get_fields(self):
        fields = super().get_fields()

        # replace serializers with id field with default PrimaryKeyRelatedField
        if (
            "request" in self.context
            and self.context["request"].method not in SAFE_METHODS
        ):
            _declared_fields, self._declared_fields = self._declared_fields, []
            self._declared_fields = {
                key: field
                for key, field in _declared_fields.items()
                if not self.is_serializer_with_id(field)
            }
            without_id_serializers = super().get_fields()
            self._declared_fields = _declared_fields

            for field_name, field in list(fields.items()):
                if self.is_serializer_with_id(field):
                    fields[field_name] = without_id_serializers[field_name]

        return fields

    @staticmethod
    def extract_fields(data, fields):
        return {field: data.pop(field) for field in fields if field in data}

    @transaction.atomic
    def create(self, validated_data):
        nested_serializers = self.extract_fields(
            validated_data, self.nested_serializers.keys()
        )
        m2m_fields = self.extract_fields(validated_data, self.m2m_fields)

        instance = self.Meta.model.objects.create(**validated_data)

        for field, value in nested_serializers.items():
            if value is None:
                continue

            serializer_class, reverse_field = self.nested_serializers[field]
            serializer = serializer_class(
                data=self.initial_data[field],
                context=self.context,
                many=type(value) == list,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(**{reverse_field: instance})

        for field, value in m2m_fields.items():
            getattr(instance, field).set(value)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        m2m_fields = self.extract_fields(validated_data, self.m2m_fields)
        nested_serializers = self.extract_fields(
            validated_data, self.nested_serializers.keys()
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        for field, value in nested_serializers.items():
            serializer_class, reverse_field = self.nested_serializers[field]
            nested_instance = getattr(instance, field, None)

            if value is None:
                if nested_instance is not None:
                    nested_instance.delete()
                continue

            serializer = serializer_class(
                instance=nested_instance,
                data=self.initial_data[field],
                context=self.context,
                many=type(value) == list,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(**{reverse_field: instance})

        for attr, value in m2m_fields.items():
            getattr(instance, attr).set(value)

        instance.save()

        return instance


class BaseAddressSerializer(ModelSerializer):
    region = RegionSerializer(read_only=True)

    class Meta:
        fields = (
            "street",
            "city",
            "zip_code",
            "region",
        )


class BaseContactSerializer(ModelSerializer):
    class Meta:
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
        )


class DonationSerializer(ModelSerializer):
    donation_source = DonationSourceCategorySerializer()

    class Meta:
        model = Donation
        fields = (
            "donated_at",
            "amount",
            "donation_source",
        )


class DonorSerializer(ModelSerializer):
    variable_symbols = SlugRelatedField(
        slug_field="variable_symbol", read_only=True, many=True
    )
    donations = DonationSerializer(many=True, read_only=True)

    class Meta:
        model = Donor
        fields = (
            "subscribed_to_newsletter",
            "is_public",
            "date_joined",
            "regional_center_support",
            "basic_section_support",
            "variable_symbols",
            "donations",
        )
        read_only_fields = "id", "date_joined"


class OfferedHelpSerializer(ModelSerializer):
    programs = EventProgramCategorySerializer(many=True)
    organizer_roles = OrganizerRoleCategorySerializer(many=True)
    team_roles = TeamRoleCategorySerializer(many=True)

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


class UserAddressSerializer(BaseAddressSerializer):
    class Meta(BaseAddressSerializer.Meta):
        model = UserAddress


class UserContactAddressSerializer(BaseAddressSerializer):
    class Meta(BaseAddressSerializer.Meta):
        model = UserContactAddress


class EYCACardSerializer(ModelSerializer):
    class Meta:
        model = EYCACard
        fields = (
            "number",
            "submitted_for_creation",
            "sent_to_user",
            "valid_till",
        )
        read_only_fields = (
            "number",
            "submitted_for_creation",
            "sent_to_user",
            "valid_till",
        )


class MembershipSerializer(ModelSerializer):
    category = MembershipCategorySerializer()

    class Meta:
        model = Membership
        fields = (
            "category",
            "administration_unit",
            "year",
        )


class QualificationResponsibleUserSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = User


class QualificationSerializer(ModelSerializer):
    approved_by = QualificationResponsibleUserSerializer()

    category = QualificationCategorySerializer()

    class Meta:
        model = Qualification
        fields = (
            "category",
            "valid_since",
            "valid_till",
            "approved_by",
        )


class QualificationNoteSerializer(ModelSerializer):
    created_by = QualificationResponsibleUserSerializer()

    class Meta:
        model = QualificationNote
        fields = (
            "created_at",
            "created_by",
            "note",
        )


class ClosePersonSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = UserClosePerson


class UserSerializer(ModelSerializer):
    all_emails = SlugRelatedField(slug_field="email", many=True, read_only=True)
    close_person = ClosePersonSerializer(allow_null=True)
    donor = DonorSerializer(allow_null=True)
    offers = OfferedHelpSerializer(allow_null=True)
    address = UserAddressSerializer()
    contact_address = UserContactAddressSerializer(allow_null=True)
    memberships = MembershipSerializer(many=True, read_only=True)
    qualifications = QualificationSerializer(many=True, read_only=True)
    qualification_notes = QualificationNoteSerializer(many=True, read_only=True)
    display_name = SerializerMethodField()
    eyca_card = EYCACardSerializer(allow_null=True)

    health_insurance_company = HealthInsuranceCompanySerializer()
    pronoun = PronounCategorySerializer()
    roles = RoleCategorySerializer(many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "_search_id",
            "first_name",
            "last_name",
            "nickname",
            "birth_name",
            "display_name",
            "phone",
            "email",
            "all_emails",
            "birthday",
            "photo",
            "close_person",
            "subscribed_to_newsletter",
            "health_insurance_company",
            "health_issues",
            "behaviour_issues",
            "pronoun",
            "is_active",
            "is_contact_information_verified",
            "date_joined",
            "roles",
            "donor",
            "offers",
            "address",
            "contact_address",
            "eyca_card",
            "memberships",
            "qualifications",
            "qualification_notes",
        )
        read_only_fields = "date_joined", "is_active", "roles"

    def update(self, instance, validated_data):
        email = validated_data.get("email")
        if email and email != instance.email:
            user = self.context["request"].user
            if instance != user:
                if user.is_superuser:
                    pass
                elif user.is_office_worker:
                    if instance.is_superuser:
                        raise ValidationError(
                            "Cannot change email of superuser as office worker"
                        )
                elif user.is_board_member:
                    if instance.is_superuser or instance.is_office_worker:
                        raise ValidationError(
                            "Cannot change email of superuser or office worker as board member"
                        )
                    if instance.is_board_member:
                        for user_administration_unit in user.administration_units.all():
                            for (
                                instance_administration_unit
                            ) in instance.administration_units.all():
                                if (
                                    user_administration_unit
                                    == instance_administration_unit
                                ):
                                    break
                            else:
                                raise ValidationError(
                                    "Cannot change email of board member of different administration unit then yours"
                                )
                elif user.is_organizer:
                    if (
                        instance.is_superuser
                        or instance.is_office_worker
                        or instance.is_board_member
                    ):
                        raise ValidationError(
                            "Cannot change email of superuser, office worker or board member as "
                            "organizer"
                        )

        return super().update(instance, validated_data)

    def get_excluded_fields(self, fields):
        if self.context["request"].user.id != fields.get("id"):
            return ["donor"]

        return []

    def get_display_name(self, instance) -> str:
        return str(instance)


class FinanceSerializer(ModelSerializer):
    grant_category = GrantCategorySerializer()

    class Meta:
        model = EventFinance
        fields = (
            "bank_account_number",
            "grant_category",
            "grant_amount",
            "total_event_cost",
            "budget",
        )


class VIPPropagationSerializer(ModelSerializer):
    class Meta:
        model = VIPEventPropagation
        fields = (
            "goals_of_event",
            "program",
            "short_invitation_text",
            "rover_propagation",
        )


class PropagationSerializer(ModelSerializer):
    diets = DietCategorySerializer(many=True)

    class Meta:
        model = EventPropagation
        fields = (
            "is_shown_on_web",
            "minimum_age",
            "maximum_age",
            "cost",
            "accommodation",
            "working_hours",
            "working_days",
            "diets",
            "organizers",
            "web_url",
            "_contact_url",
            "invitation_text_introduction",
            "invitation_text_practical_information",
            "invitation_text_work_description",
            "invitation_text_about_us",
            "contact_name",
            "contact_phone",
            "contact_email",
        )


class QuestionnaireSerializer(ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = (
            "introduction",
            "after_submit_text",
        )


class RegistrationSerializer(ModelSerializer):
    questionnaire = QuestionnaireSerializer(allow_null=True)

    class Meta:
        model = EventRegistration
        fields = (
            "is_registration_required",
            "alternative_registration_link",
            "is_event_full",
            "questionnaire",
        )


class UpdatableListSerializer(ListSerializer):
    def update(self, instance, validated_data):
        instance.all().delete()
        return self.create(validated_data)


class EventContactSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = EventContact
        list_serializer_class = UpdatableListSerializer


class FeedbackFormSerializer(ModelSerializer):
    class Meta:
        model = FeedbackForm
        fields = (
            "introduction",
            "after_submit_text",
        )


class RecordSerializer(ModelSerializer):
    contacts = EventContactSerializer(many=True, required=False)
    feedback_form = FeedbackFormSerializer(allow_null=True)

    age_stats = SerializerMethodField()

    class Meta:
        model = EventRecord
        fields = (
            "total_hours_worked",
            "comment_on_work_done",
            "participants",
            "number_of_participants",
            "number_of_participants_under_26",
            "is_event_closed_email_enabled",
            "note",
            "contacts",
            "age_stats",
            "feedback_form",
        )

    def get_age_stats(self, instance) -> dict:
        return {
            "at_start_of_event": AgeStats(
                "", instance.get_all_participants(), instance.event.start
            ).get_data(),
            "at_start_of_year": AgeStats(
                "",
                instance.get_all_participants(),
                date(instance.event.start.year, 1, 1),
            ).get_data(),
        }


class EventSerializer(ModelSerializer):
    finance = FinanceSerializer(allow_null=True)
    propagation = PropagationSerializer(allow_null=True)
    vip_propagation = VIPPropagationSerializer(allow_null=True)
    registration = RegistrationSerializer(allow_null=True)
    record = RecordSerializer(allow_null=True)

    group = EventGroupCategorySerializer()
    category = EventCategorySerializer()
    program = EventProgramCategorySerializer()
    intended_for = EventIntendedForCategorySerializer()

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "is_canceled",
            "is_closed",
            "is_archived",
            "start",
            "start_time",
            "end",
            "number_of_sub_events",
            "location",
            "online_link",
            "group",
            "category",
            "tags",
            "program",
            "intended_for",
            "administration_units",
            "main_organizer",
            "other_organizers",
            "is_attendance_list_required",
            "internal_note",
            "duration",
            "finance",
            "propagation",
            "vip_propagation",
            "registration",
            "record",
        )
        read_only_fields = ["duration"]

    def get_excluded_fields(self, fields):
        if self.context["request"].user.is_member_only:
            return ["internal_note", "finance", "record"]

        return []

    def create(self, validated_data):
        user = self.context["request"].user
        if validated_data["end"].year <= get_locked_year():
            if not user.is_superuser and not user.is_office_worker:
                raise DjangoValidationError("Nemůžeš vytvářet události v minulosti")

        validated_data["created_by"] = user
        instance = super().create(validated_data)

        if self.context["request"].user != instance.main_organizer:
            emails.event_created(instance)

        if (
            instance.main_organizer.id == "1e82e062-9fd0-4f1a-af14-6d3645b1195a"
            or instance.administration_units.filter(id=8).exists()
        ):  # robby nebo modry kamen
            emails.text(
                ["bis@brontosaurus.cz"],
                "Robby nebo Modrý kámen vytvořil novou akci",
                f"Najdeš ji https://bis.brontosaurus.cz/admin/bis/event/{instance.id}/change/",
            )

        return instance

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if validated_data.get("end") and instance.end != validated_data["end"]:
            if validated_data["end"].year <= get_locked_year():
                if not user.is_superuser and not user.is_office_worker:
                    raise DjangoValidationError(
                        "Nemůžeš změnit datum události do minulosti"
                    )

        is_closing = not instance.is_closed and validated_data.get("is_closed")
        had_attendance = EventAttendanceListPage.objects.filter(
            record__event=instance
        ).exists()
        had_photos = EventPhoto.objects.filter(record__event=instance).exists()
        if is_closing:
            validated_data["closed_at"] = date.today()

        instance = super().update(instance, validated_data)
        if is_closing:
            emails.event_end_participants_notification(instance)

        has_attendance = EventAttendanceListPage.objects.filter(
            record__event=instance
        ).exists()
        has_photos = EventPhoto.objects.filter(record__event=instance).exists()

        if (not had_attendance and has_attendance) or (not had_photos and has_photos):
            emails.event_attendance_or_photos_notification(instance)

        return instance


class LocationContactPersonSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = LocationContactPerson


class LocationPatronSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = LocationPatron


class LocationSerializer(ModelSerializer):
    patron = LocationPatronSerializer(allow_null=True)
    contact_person = LocationContactPersonSerializer(allow_null=True)

    program = LocationProgramCategorySerializer()
    accessibility_from_prague = LocationAccessibilityCategorySerializer()
    accessibility_from_brno = LocationAccessibilityCategorySerializer()
    region = RegionSerializer()

    class Meta:
        model = Location
        fields = (
            "id",
            "name",
            "description",
            "patron",
            "contact_person",
            "is_traditional",
            "for_beginners",
            "is_full",
            "is_unexplored",
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
        )


class OpportunitySerializer(ModelSerializer):
    category = OpportunityCategorySerializer()
    priority = OpportunityPrioritySerializer()

    class Meta:
        model = Opportunity
        fields = (
            "id",
            "category",
            "priority",
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
        read_only_fields = ("priority",)

    def create(self, validated_data):
        validated_data["contact_person"] = User.objects.get(
            id=self.context["view"].kwargs["user_id"]
        )
        assert validated_data["contact_person"] == self.context["request"].user
        validated_data["priority"] = OpportunityPriority.objects.get(slug="normal")
        instance = super().create(validated_data)
        emails.opportunity_created(instance)
        return instance


class FinanceReceiptSerializer(ModelSerializer):
    class Meta:
        model = EventFinanceReceipt
        fields = (
            "id",
            "receipt",
        )

    @catch_related_object_does_not_exist
    def create(self, validated_data):
        validated_data["finance"] = Event.objects.get(
            id=self.context["view"].kwargs["event_id"]
        ).finance
        return super().create(validated_data)


class EventPropagationImageSerializer(ModelSerializer):
    class Meta:
        model = EventPropagationImage
        fields = (
            "id",
            "order",
            "image",
        )

    @catch_related_object_does_not_exist
    def create(self, validated_data):
        validated_data["propagation"] = Event.objects.get(
            id=self.context["view"].kwargs["event_id"]
        ).propagation
        return super().create(validated_data)


class EventPhotoSerializer(ModelSerializer):
    class Meta:
        model = EventPhoto
        fields = (
            "id",
            "photo",
        )

    @catch_related_object_does_not_exist
    def create(self, validated_data):
        validated_data["record"] = Event.objects.get(
            id=self.context["view"].kwargs["event_id"]
        ).record
        return super().create(validated_data)


class AttendanceListPageSerializer(ModelSerializer):
    class Meta:
        model = EventAttendanceListPage
        fields = (
            "id",
            "page",
        )

    @catch_related_object_does_not_exist
    def create(self, validated_data):
        validated_data["record"] = Event.objects.get(
            id=self.context["view"].kwargs["event_id"]
        ).record
        return super().create(validated_data)


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "question",
            "data",
            "is_required",
            "order",
        )

    @catch_related_object_does_not_exist
    def create(self, validated_data):
        validated_data["questionnaire"] = Event.objects.get(
            id=self.context["view"].kwargs["event_id"]
        ).registration.questionnaire
        return super().create(validated_data)


class EventApplicationClosePersonSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = EventApplicationClosePerson


class EventApplicationAddressSerializer(BaseAddressSerializer):
    class Meta(BaseAddressSerializer.Meta):
        model = EventApplicationAddress


class AnswerSerializer(ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = Answer
        fields = (
            "question",
            "answer",
            "data",
        )


class EventApplicationSerializer(ModelSerializer):
    close_person = EventApplicationClosePersonSerializer(allow_null=True)
    address = EventApplicationAddressSerializer(allow_null=True)
    answers = AnswerSerializer(many=True)

    pronoun = PronounCategorySerializer()

    class Meta:
        model = EventApplication
        fields = (
            "id",
            "user",
            "state",
            "first_name",
            "last_name",
            "nickname",
            "phone",
            "email",
            "birthday",
            "health_issues",
            "pronoun",
            "created_at",
            "close_person",
            "address",
            "answers",
            "note",
            "internal_note",
            "paid_for",
            "is_child_application",
        )

    @catch_related_object_does_not_exist
    def create(self, validated_data):
        validated_data["event_registration"] = Event.objects.get(
            id=self.context["view"].kwargs["event_id"]
        ).registration
        instance = super().create(validated_data)
        emails.application_created(instance)
        return instance

    @catch_related_object_does_not_exist
    def update(self, instance, validated_data):
        if not all(
            [
                key in ["user", "state", "internal_note", "paid_for"]
                for key in validated_data
            ]
        ):
            raise ValidationError(
                "Only user, state, paid_for and internal_note are editable"
            )
        return super().update(instance, validated_data)


class InquirySerializer(ModelSerializer):
    class Meta:
        model = Inquiry
        fields = (
            "id",
            "inquiry",
            "slug",
            "data",
            "is_required",
            "order",
        )

    @catch_related_object_does_not_exist
    def create(self, validated_data):
        validated_data["feedback_form"] = Event.objects.get(
            id=self.context["view"].kwargs["event_id"]
        ).record.feedback_form
        return super().create(validated_data)


class ReplySerializer(ModelSerializer):
    inquiry = InquirySerializer()

    class Meta:
        model = Reply
        fields = (
            "inquiry",
            "reply",
            "data",
        )


class EventFeedbackSerializer(ModelSerializer):
    replies = ReplySerializer(many=True)

    class Meta:
        model = EventFeedback
        fields = (
            "id",
            "user",
            "name",
            "email",
            "created_at",
            "note",
            "replies",
        )

    @catch_related_object_does_not_exist
    def create(self, validated_data):
        validated_data["event_record"] = Event.objects.get(
            id=self.context["view"].kwargs["event_id"]
        ).record
        instance = super().create(validated_data)
        emails.feedback_created(instance)
        return instance


class UserSearchSerializer(ModelSerializer):
    display_name = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "_search_id",
            "display_name",
            "first_name",
            "last_name",
        )

    def get_display_name(self, instance) -> str:
        return str(instance)


class EventDraftSerializer(ModelSerializer):
    class Meta:
        model = EventDraft
        fields = (
            "id",
            "data",
        )

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class DashboardItemSerializer(ModelSerializer):
    class Meta:
        model = DashboardItem
        fields = "visible_date", "date", "name", "description"


class GetUnknownUserRequestSerializer(Serializer):
    first_name = CharField()
    last_name = CharField()
    birthday = DateField()


class GetUserByEmailRequestSerializer(Serializer):
    email = CharField(min_length=3)


class GetUserByEmailResponseSerializer(Serializer):
    first_name = CharField(required=False)
    last_name = CharField(required=False)
    phone = CharField(required=False)
    message = CharField()
    count = IntegerField()


class GetAttendanceListRequestSerializer(Serializer):
    formatting = ChoiceField(["pdf", "xlsx"], default="pdf")


class GetParticipantsListRequestSerializer(Serializer):
    formatting = ChoiceField(["pdf", "xlsx"], default="pdf")


class EventRouterKwargsSerializer(Serializer):
    event_id = IntegerField()


class ApplicationRouterKwargsSerializer(Serializer):
    event_id = IntegerField()
    application_id = IntegerField()


class UserRouterKwargsSerializer(Serializer):
    user_id = UUIDField()
