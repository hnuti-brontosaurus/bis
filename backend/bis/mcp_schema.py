"""GraphQL schema for BIS MCP tools.

Health data is never exposed. Personal data (names, emails, phones, birthdays,
addresses, notes) is exposed only to accounts whose MCPAccess allows it, set
for an LLM provider with a data processing agreement; every other account,
staff included, sees people as anonymous UserType rows (id, birth year,
region, memberships, ...). Documents
and photos that carry personal data are left out for everyone.

Filters, ordering and aggregate paths may only touch fields the account can
see, since matching on a value reveals it as surely as returning it.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

import strawberry
import strawberry_django
from administration_units.models import (
    AdministrationSubUnit,
    AdministrationSubUnitAddress,
    AdministrationUnit,
    AdministrationUnitAddress,
    GeneralMeeting,
)
from bis.models import (
    Location,
    LocationPhoto,
    Membership,
    Qualification,
    QualificationNote,
    User,
    UserAddress,
)
from bis.permissions import Permissions
from categories.models import (
    AdministrationUnitCategory,
    DietCategory,
    DonationSourceCategory,
    DonorEventCategory,
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
    EventTag,
    GrantCategory,
    HealthInsuranceCompany,
    LocationAccessibilityCategory,
    LocationProgramCategory,
    MembershipCategory,
    OpportunityCategory,
    OpportunityPriority,
    OrganizerRoleCategory,
    PronounCategory,
    QualificationCategory,
    RoleCategory,
    TeamRoleCategory,
)
from common.sensitivity import Sensitivity
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, FieldError
from django.db.models import (
    Avg,
    Case,
    Count,
    DateField,
    F,
    JSONField,
    Max,
    Min,
    Sum,
    When,
)
from donations.models import Donation, Donor, DonorEvent, FundraisingCampaign, Pledge
from event.models import (
    Event,
    EventFinance,
    EventPropagation,
    EventPropagationImage,
    EventRecord,
    EventRegistration,
    VIPEventPropagation,
)
from feedback.models import EventFeedback, FeedbackForm, Inquiry, Reply
from graphql import GraphQLError, ValidationRule
from opportunities.models import OfferedHelp, Opportunity
from other.models import UserTag
from phonenumber_field.modelfields import PhoneNumberField
from questionnaire.models import (
    Answer,
    EventApplication,
    EventApplicationAddress,
    Question,
    Questionnaire,
)
from regions.models import Region
from strawberry import auto
from strawberry.extensions import SchemaExtension
from strawberry.scalars import JSON
from strawberry_django.fields.types import field_type_map
from strawberry_django.optimizer import DjangoOptimizerExtension
from tinymce.models import HTMLField

MAX_ROWS = 1000

field_type_map[HTMLField] = str
field_type_map[PhoneNumberField] = str

PERSONAL = "personal"


def visible_sensitivities(user):
    if user.sees_personal_data_over_mcp:
        return [Sensitivity.NONE, Sensitivity.PERSONAL]
    return [Sensitivity.NONE]


def personal():
    return strawberry_django.field(
        metadata={PERSONAL: True},
        description="Personal data, not available to every account.",
    )


class _PersonalDataRule(ValidationRule):
    def enter_field(self, node, *args):
        field = self.context.get_field_def()
        definition = field and field.extensions.get("strawberry-definition")
        if definition and definition.metadata.get(PERSONAL):
            name = f"{self.context.get_parent_type().name}.{node.name.value}"
            self.report_error(
                GraphQLError(
                    f"{name} is personal data, not available to this account.",
                    node,
                )
            )


class HidePersonalData(SchemaExtension):
    def on_operation(self):
        if not self.execution_context.context[
            "request"
        ].user.sees_personal_data_over_mcp:
            self.execution_context.validation_rules += (_PersonalDataRule,)
        yield


def _media_url(file):
    return f"{settings.FULL_HOSTNAME}{file.url}" if file else None


def _category_type(model, exclude=None):
    name = f"{model.__name__}Type"
    options = {"exclude": exclude} if exclude else {"fields": "__all__"}
    return strawberry_django.type(model, name=name, **options)(type(name, (), {}))


EventCategoryType = _category_type(EventCategory)
EventGroupCategoryType = _category_type(EventGroupCategory)
EventProgramCategoryType = _category_type(EventProgramCategory, exclude=["email"])
EventIntendedForCategoryType = _category_type(EventIntendedForCategory)
EventTagType = _category_type(EventTag)
GrantCategoryType = _category_type(GrantCategory)
DietCategoryType = _category_type(DietCategory)
QualificationCategoryType = _category_type(QualificationCategory)
AdministrationUnitCategoryType = _category_type(AdministrationUnitCategory)
MembershipCategoryType = _category_type(MembershipCategory)
DonationSourceCategoryType = _category_type(
    DonationSourceCategory, exclude=["_import_id"]
)
OrganizerRoleCategoryType = _category_type(OrganizerRoleCategory)
TeamRoleCategoryType = _category_type(TeamRoleCategory)
OpportunityCategoryType = _category_type(OpportunityCategory)
OpportunityPriorityType = _category_type(OpportunityPriority)
LocationProgramCategoryType = _category_type(LocationProgramCategory)
LocationAccessibilityCategoryType = _category_type(LocationAccessibilityCategory)
RoleCategoryType = _category_type(RoleCategory)
HealthInsuranceCompanyType = _category_type(HealthInsuranceCompany)
PronounCategoryType = _category_type(PronounCategory)
DonorEventCategoryType = _category_type(DonorEventCategory)
FundraisingCampaignType = _category_type(FundraisingCampaign)


@strawberry_django.type(Region, exclude=["area"])
class RegionType:
    pass


# Person models list their fields explicitly, so a field added to the model
# later stays hidden until someone decides whether it is personal data.


@strawberry_django.type(
    User,
    fields=[
        "id",
        "is_active",
        "date_joined",
        "subscription_status",
        "is_contact_information_verified",
    ],
)
class UserType:
    office_workers_note: auto = personal()
    first_name: auto = personal()
    last_name: auto = personal()
    nickname: auto = personal()
    birth_name: auto = personal()
    vokativ: auto = personal()
    phone: auto = personal()
    email: auto = personal()
    birthday: auto = personal()
    health_insurance_company: HealthInsuranceCompanyType | None
    pronoun: PronounCategoryType | None
    roles: list[RoleCategoryType]
    address: UserAddressType | None
    tags: list[UserTagType]
    memberships: list[MembershipType]
    qualifications: list[QualificationType]
    qualification_notes: list[QualificationNoteType]
    participated_in_events: list[EventRecordType]
    events_where_was_as_main_organizer: list[EventType]
    events_where_was_organizer: list[EventType]
    applications: list[EventApplicationType]
    donor: DonorType | None
    offers: OfferedHelpType | None

    @strawberry_django.field(only=["birthday"])
    def birth_year(self) -> int | None:
        return self.birthday.year if self.birthday else None


@strawberry_django.type(UserAddress, fields=["region"])
class UserAddressType:
    region: RegionType | None
    street: auto = personal()
    city: auto = personal()
    zip_code: auto = personal()


@strawberry_django.type(UserTag, exclude=["users"])
class UserTagType:
    pass


@strawberry_django.type(Membership, exclude=["_year", "_import_id"])
class MembershipType:
    user: UserType
    category: MembershipCategoryType
    administration_unit: AdministrationUnitType


@strawberry_django.type(Qualification, exclude=["_import_id"])
class QualificationType:
    user: UserType
    category: QualificationCategoryType
    approved_by: UserType | None


@strawberry_django.type(QualificationNote, exclude=["education_members_note"])
class QualificationNoteType:
    education_members_note: auto = personal()
    user: UserType
    created_by: UserType


@strawberry_django.type(OfferedHelp, fields="__all__")
class OfferedHelpType:
    user: UserType
    programs: list[EventProgramCategoryType]
    organizer_roles: list[OrganizerRoleCategoryType]
    team_roles: list[TeamRoleCategoryType]


@strawberry_django.type(LocationPhoto, fields=["id"])
class LocationPhotoType:
    @strawberry_django.field(only=["photo"])
    def url(self) -> str | None:
        return _media_url(self.photo)


@strawberry_django.type(
    Location,
    exclude=["gps_location", "address", "_import_id", "_search_field"],
)
class LocationType:
    program: LocationProgramCategoryType | None
    accessibility_from_prague: LocationAccessibilityCategoryType | None
    accessibility_from_brno: LocationAccessibilityCategoryType | None
    region: RegionType | None
    photos: list[LocationPhotoType]

    @strawberry_django.field(only=["gps_location"])
    def latitude(self) -> float | None:
        return self.gps_location.y if self.gps_location else None

    @strawberry_django.field(only=["gps_location"])
    def longitude(self) -> float | None:
        return self.gps_location.x if self.gps_location else None


@strawberry_django.type(AdministrationUnitAddress, fields=["region"])
class AdministrationUnitAddressType:
    region: RegionType | None


@strawberry_django.type(GeneralMeeting, fields="__all__")
class GeneralMeetingType:
    pass


@strawberry_django.type(AdministrationSubUnitAddress, fields=["region"])
class AdministrationSubUnitAddressType:
    region: RegionType | None


@strawberry_django.type(
    AdministrationSubUnit,
    exclude=["gps_location", "phone", "email", "_history"],
)
class AdministrationSubUnitType:
    phone: auto = personal()
    email: auto = personal()
    main_leader: UserType
    sub_leaders: list[UserType]
    address: AdministrationSubUnitAddressType | None


@strawberry_django.type(
    AdministrationUnit,
    exclude=[
        "gps_location",
        "image",
        "custom_statues",
        "phone",
        "email",
        "_import_id",
        "_history",
        "_search_field",
    ],
)
class AdministrationUnitType:
    phone: auto = personal()
    email: auto = personal()
    category: AdministrationUnitCategoryType
    chairman: UserType | None
    vice_chairman: UserType | None
    manager: UserType | None
    board_members: list[UserType]
    address: AdministrationUnitAddressType | None
    sub_units: list[AdministrationSubUnitType]
    general_meetings: list[GeneralMeetingType]

    @strawberry_django.field(only=["gps_location"])
    def latitude(self) -> float | None:
        return self.gps_location.y if self.gps_location else None

    @strawberry_django.field(only=["gps_location"])
    def longitude(self) -> float | None:
        return self.gps_location.x if self.gps_location else None


@strawberry_django.type(FeedbackForm, fields="__all__")
class FeedbackFormType:
    inquiries: list[InquiryType]


@strawberry_django.type(Inquiry, exclude=["sensitivity"])
class InquiryType:
    replies: list[ReplyType]


@strawberry_django.type(Reply, fields=["id", "feedback"])
class ReplyType:
    inquiry: InquiryType

    @strawberry_django.field(
        only=["reply", "inquiry__sensitivity"], select_related=["inquiry"]
    )
    def reply(self, info: strawberry.Info) -> str | None:
        return self.reply if _answer_visible(info, self.inquiry) else None

    @strawberry_django.field(
        only=["value", "inquiry__sensitivity"], select_related=["inquiry"]
    )
    def value(self, info: strawberry.Info) -> JSON | None:
        return self.value if _answer_visible(info, self.inquiry) else None

    @strawberry_django.field(
        only=["data", "inquiry__sensitivity"], select_related=["inquiry"]
    )
    def data(self, info: strawberry.Info) -> JSON | None:
        return self.data if _answer_visible(info, self.inquiry) else None


@strawberry_django.type(EventFeedback, exclude=["name", "email"])
class EventFeedbackType:
    name: auto = personal()
    email: auto = personal()
    event: EventType
    user: UserType | None
    replies: list[ReplyType]


@strawberry_django.type(EventFinance, exclude=["bank_account_number", "budget"])
class EventFinanceType:
    bank_account_number: auto = personal()
    grant_category: GrantCategoryType | None


@strawberry_django.type(EventPropagationImage, fields=["id", "order"])
class EventPropagationImageType:
    @strawberry_django.field(only=["image"])
    def url(self) -> str | None:
        return _media_url(self.image)


@strawberry_django.type(
    EventPropagation,
    exclude=[
        "organizers",
        "contact_name",
        "contact_phone",
        "contact_email",
        "_contact_url",
    ],
)
class EventPropagationType:
    organizers: auto = personal()
    contact_name: auto = personal()
    contact_phone: auto = personal()
    contact_email: auto = personal()
    diets: list[DietCategoryType]
    images: list[EventPropagationImageType]


@strawberry_django.type(VIPEventPropagation, fields="__all__")
class VIPEventPropagationType:
    pass


def _answer_visible(info, question):
    """Answers are shown only once their question is classified, see
    common/sensitivity.py."""
    user = info.context["request"].user
    return question.sensitivity in visible_sensitivities(user)


@strawberry_django.type(Answer, fields=["id", "application"])
class AnswerType:
    question: QuestionType

    @strawberry_django.field(
        only=["answer", "question__sensitivity"], select_related=["question"]
    )
    def answer(self, info: strawberry.Info) -> str | None:
        return self.answer if _answer_visible(info, self.question) else None

    @strawberry_django.field(
        only=["data", "question__sensitivity"], select_related=["question"]
    )
    def data(self, info: strawberry.Info) -> JSON | None:
        return self.data if _answer_visible(info, self.question) else None


@strawberry_django.type(Question, exclude=["sensitivity"])
class QuestionType:
    answers: list[AnswerType]


@strawberry_django.type(Questionnaire, fields="__all__")
class QuestionnaireType:
    questions: list[QuestionType]


@strawberry_django.type(EventApplicationAddress, fields=["region"])
class EventApplicationAddressType:
    region: RegionType | None
    street: auto = personal()
    city: auto = personal()
    zip_code: auto = personal()


@strawberry_django.type(
    EventApplication,
    fields=[
        "id",
        "state",
        "is_child_application",
        "created_at",
        "paid_for",
    ],
)
class EventApplicationType:
    applicant_note: auto = personal()
    first_name: auto = personal()
    last_name: auto = personal()
    nickname: auto = personal()
    phone: auto = personal()
    email: auto = personal()
    birthday: auto = personal()
    event_registration: EventRegistrationType
    user: UserType | None
    pronoun: PronounCategoryType | None
    address: EventApplicationAddressType | None
    answers: list[AnswerType]

    @strawberry_django.field(only=["birthday"])
    def birth_year(self) -> int | None:
        return self.birthday.year if self.birthday else None


@strawberry_django.type(EventRegistration, fields="__all__")
class EventRegistrationType:
    questionnaire: QuestionnaireType | None
    applications: list[EventApplicationType]


@strawberry_django.type(EventRecord, fields="__all__")
class EventRecordType:
    participants: list[UserType]

    @strawberry_django.field(
        prefetch_related=["participants", "event__other_organizers"],
    )
    def participants_count(self) -> int:
        return self.get_participants_count()

    @strawberry_django.field(
        prefetch_related=["participants", "event__other_organizers"],
    )
    def young_participants_count(self) -> int:
        return self.get_young_participants_count()


@strawberry_django.type(
    Event, exclude=["organizers_note", "_import_id", "_search_field"]
)
class EventType:
    organizers_note: auto = personal()
    location: LocationType | None
    category: EventCategoryType
    group: EventGroupCategoryType
    program: EventProgramCategoryType
    intended_for: EventIntendedForCategoryType
    tags: list[EventTagType]
    administration_units: list[AdministrationUnitType]
    main_organizer: UserType | None
    other_organizers: list[UserType]
    created_by: UserType | None
    finance: EventFinanceType | None
    propagation: EventPropagationType | None
    vip_propagation: VIPEventPropagationType | None
    registration: EventRegistrationType | None
    record: EventRecordType | None
    feedback_form: FeedbackFormType | None
    feedbacks: list[EventFeedbackType]


@strawberry_django.type(
    Opportunity,
    exclude=[
        "contact_name",
        "contact_phone",
        "contact_email",
        "image",
        "_search_field",
    ],
)
class OpportunityType:
    contact_name: auto = personal()
    contact_phone: auto = personal()
    contact_email: auto = personal()
    category: OpportunityCategoryType
    priority: OpportunityPriorityType
    location: LocationType
    contact_person: UserType

    @strawberry_django.field(only=["image"])
    def image_url(self) -> str | None:
        return _media_url(self.image)


@strawberry_django.type(Pledge, fields="__all__")
class PledgeType:
    donor: DonorType
    donation_source: DonationSourceCategoryType


@strawberry_django.type(Donation, exclude=["info", "_variable_symbol", "_import_id"])
class DonationType:
    info: auto = personal()
    donor: DonorType | None
    pledge: PledgeType | None
    donation_source: DonationSourceCategoryType


@strawberry_django.type(DonorEvent, exclude=["fundraisers_note"])
class DonorEventType:
    fundraisers_note: auto = personal()
    donor: DonorType
    event_type: DonorEventCategoryType
    campaign: FundraisingCampaignType | None
    created_by: UserType | None


@strawberry_django.type(
    Donor,
    fields=[
        "id",
        "subscribed_to_newsletter",
        "is_public",
        "do_not_call",
        "do_not_solicit",
        "date_joined",
    ],
)
class DonorType:
    fundraisers_note: auto = personal()
    user: UserType
    regional_center_support: AdministrationUnitType | None
    basic_section_support: AdministrationUnitType | None
    donations: list[DonationType]
    pledges: list[PledgeType]
    events: list[DonorEventType]


# Root datasets: GraphQL field name -> model. Also the choices of `aggregate`.
DATASETS = {
    "events": Event,
    "feedbacks": EventFeedback,
    "event_applications": EventApplication,
    "users": User,
    "memberships": Membership,
    "donors": Donor,
    "donations": Donation,
    "opportunities": Opportunity,
    "locations": Location,
    "administration_units": AdministrationUnit,
}

Dataset = strawberry.enum(
    Enum("Dataset", {name.upper(): name for name in DATASETS}),
    description="Root dataset to aggregate over.",
)

# Computed fields usable in aggregate paths; each maps to a coarse ORM
# expression so the underlying personal column itself is never grouped on.
AGGREGATE_ALIASES = {
    User: {"birth_year": "birthday__year"},
    EventApplication: {"birth_year": "birthday__year"},
}

# Answer fields shown per row by their question's sensitivity: aggregates see
# them through the same condition as _answer_visible, filters not at all.
MASKED_ANSWERS = {
    Answer: ("question", {"answer", "data"}),
    Reply: ("inquiry", {"reply", "value", "data"}),
}

DATE_TRANSFORMS = {"year", "iso_year", "quarter", "month", "week", "week_day", "day"}


def _permitted(info, model):
    user = info.context["request"].user
    queryset = model.objects.all()
    if user.is_bot:
        # Bots have no roles, so per-user Permissions filtering would hide
        # everything; the bot account gets full read visibility instead.
        return queryset
    return Permissions(user, model, "backend").filter_queryset(queryset)


def _visible(model, name, user):
    fields = EXPOSED_FIELDS.get(model, {})
    return name in fields and (not fields[name] or user.sees_personal_data_over_mcp)


def _check_lookup(model, lookup, user):
    """Allow a filter or ordering only along fields the account can see."""
    field = None
    for part in lookup.split("__"):
        if _visible(model, part, user):
            field = model._meta.get_field(part)
            if not field.is_relation:
                return
            model = field.related_model
        elif field and field.get_lookup(part):
            return
        else:
            raise ValueError(f"Invalid lookup {lookup}: {part} is not exposed")


def _apply_filters(info, queryset, filters):
    if not filters:
        return queryset
    for lookup in filters:
        _check_lookup(queryset.model, lookup, info.context["request"].user)
    try:
        return queryset.filter(**filters)
    except (FieldError, TypeError, ValueError) as e:
        raise ValueError(f"Invalid filter: {e}")


def _list(info, dataset, filters, ordering, limit, offset):
    model = DATASETS[dataset]
    queryset = _apply_filters(info, _permitted(info, model), filters)
    if ordering:
        for lookup in ordering:
            _check_lookup(model, lookup.removeprefix("-"), info.context["request"].user)
        queryset = queryset.order_by(*ordering)
    if info.context.get("_export"):
        from xlsx_export.export import EXPORT_SERIALIZERS

        if model not in EXPORT_SERIALIZERS:
            raise ValueError(f"{dataset} cannot be exported")
        info.context["_export_qs"][dataset] = queryset
        return []
    if limit > MAX_ROWS:
        raise ValueError(f"limit must be at most {MAX_ROWS}, use offset to page")
    return queryset[offset : offset + limit]


def _exposed_fields():
    exposed = {}
    for type_ in list(globals().values()):
        definition = getattr(type_, "__strawberry_django_definition__", None)
        if definition is None:
            continue
        # value: whether the field is personal data
        exposed[definition.model] = {
            field.django_name: bool(field.metadata.get(PERSONAL))
            for field in type_.__strawberry_definition__.fields
            if field.base_resolver is None
        }
    return exposed


def _aggregate_expression(model, path, user):
    """Translate a `__`-separated aggregate path into an ORM expression,
    allowing only fields the account can see, so grouping cannot reveal hidden
    values."""
    parts = path.split("__")
    for index, part in enumerate(parts):
        rest = parts[index + 1 :]
        alias = AGGREGATE_ALIASES.get(model, {}).get(part)
        if alias:
            if rest:
                raise ValueError(f"Invalid path {path}: nothing may follow {part}")
            return F("__".join([*parts[:index], alias]))
        question, masked = MASKED_ANSWERS.get(model, (None, set()))
        if part in masked:
            if rest and not isinstance(model._meta.get_field(part), JSONField):
                raise ValueError(
                    f"Invalid path {path}: unsupported lookup after {part}"
                )
            sensitivity = "__".join([*parts[:index], question, "sensitivity", "in"])
            return Case(
                When(**{sensitivity: visible_sensitivities(user)}, then=F(path))
            )
        if not _visible(model, part, user):
            raise ValueError(f"Invalid path {path}: {part} is not exposed")
        try:
            field = model._meta.get_field(part)
        except FieldDoesNotExist:
            raise ValueError(f"Invalid path {path}: {part} is not a model field")
        if field.is_relation:
            model = field.related_model
            continue
        if not rest or isinstance(field, JSONField):
            return F(path)
        if isinstance(field, DateField) and len(rest) == 1:
            if rest[0] in DATE_TRANSFORMS:
                return F(path)
        raise ValueError(f"Invalid path {path}: unsupported lookup after {part}")
    return F(path)


def _jsonable(value):
    if isinstance(value, (date, UUID)):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    return value


@strawberry.type
class Query:
    @strawberry.field
    def events(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EventType]:
        return _list(info, "events", filters, ordering, limit, offset)

    @strawberry.field
    def event(self, info: strawberry.types.Info, event_id: int) -> EventType | None:
        return _permitted(info, Event).filter(id=event_id).first()

    @strawberry.field
    def feedbacks(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EventFeedbackType]:
        return _list(info, "feedbacks", filters, ordering, limit, offset)

    @strawberry.field
    def event_applications(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EventApplicationType]:
        return _list(info, "event_applications", filters, ordering, limit, offset)

    @strawberry.field
    def users(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UserType]:
        return _list(info, "users", filters, ordering, limit, offset)

    @strawberry.field
    def memberships(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MembershipType]:
        return _list(info, "memberships", filters, ordering, limit, offset)

    @strawberry.field
    def donors(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DonorType]:
        return _list(info, "donors", filters, ordering, limit, offset)

    @strawberry.field
    def donations(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DonationType]:
        return _list(info, "donations", filters, ordering, limit, offset)

    @strawberry.field
    def opportunities(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OpportunityType]:
        return _list(info, "opportunities", filters, ordering, limit, offset)

    @strawberry.field
    def locations(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[LocationType]:
        return _list(info, "locations", filters, ordering, limit, offset)

    @strawberry.field
    def administration_units(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AdministrationUnitType]:
        return _list(info, "administration_units", filters, ordering, limit, offset)

    @strawberry.field
    def aggregate(
        self,
        info: strawberry.types.Info,
        dataset: Dataset,
        filters: JSON | None = None,
        group_by: list[str] | None = None,
        sum_of: list[str] | None = None,
        avg_of: list[str] | None = None,
        min_of: list[str] | None = None,
        max_of: list[str] | None = None,
    ) -> JSON:
        """Count rows of a dataset, optionally grouped, plus sum/avg/min/max.

        Paths use `__` and may only walk fields the schema exposes, e.g.
        group_by: ["start__year", "category__slug"],
        sum_of: ["record__total_hours_worked"].
        Date fields accept __year/__quarter/__month/... Users and applications
        also have `birth_year`. Answers and replies to a question whose
        sensitivity this account cannot see are aggregated as null. Returns
        one row per group, `count` counting distinct rows of the dataset. Joins
        over lists repeat values, so sums across a to-many path count a row
        once per related item.
        """
        model = DATASETS[dataset.value]
        user = info.context["request"].user
        queryset = _apply_filters(info, _permitted(info, model), filters)
        group_by = group_by or []
        groups = {
            f"group{i}": _aggregate_expression(model, path, user)
            for i, path in enumerate(group_by)
        }
        functions = {
            "sum": (Sum, sum_of),
            "avg": (Avg, avg_of),
            "min": (Min, min_of),
            "max": (Max, max_of),
        }
        aggregates = {"count": Count("pk", distinct=True)}
        requested = {}
        for name, (function, paths) in functions.items():
            for i, path in enumerate(paths or []):
                aggregates[f"{name}{i}"] = function(
                    _aggregate_expression(model, path, user)
                )
                requested[f"{name}{i}"] = (name, path)

        if groups:
            rows = list(
                queryset.values(**groups)
                .annotate(**aggregates)
                .order_by(*groups)[: MAX_ROWS + 1]
            )
            if len(rows) > MAX_ROWS:
                raise ValueError(f"More than {MAX_ROWS} groups, narrow the filters")
        else:
            rows = [queryset.aggregate(**aggregates)]

        result = []
        for row in rows:
            item = {
                path: _jsonable(row[f"group{i}"]) for i, path in enumerate(group_by)
            }
            item["count"] = row["count"]
            for key, (name, path) in requested.items():
                item.setdefault(name, {})[path] = _jsonable(row[key])
            result.append(item)
        return result


EXPOSED_FIELDS = _exposed_fields()

schema = strawberry.Schema(
    query=Query,
    extensions=[DjangoOptimizerExtension, HidePersonalData],
)
