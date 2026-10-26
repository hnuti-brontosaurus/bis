"""How sensitive each field of BIS data is, rendered publicly at /docs/.

Only business data is listed: framework and login tables, technical models and
the `_`-prefixed helper columns (search indexes, import ids, caches) are left
out. Every other field is listed explicitly, so a field added to a model fails
bis/tests/test_data_sensitivity.py until someone classifies it. A field gets
the strictest level of any of its uses: an organizer's email is published as
an event contact, yet stays personal, and the note says where it is published.
"""

from django.apps import apps
from django.db.models import TextChoices


class Level(TextChoices):
    PUBLIC = "public", "Veřejné"
    INTERNAL = "internal", "Interní"
    PERSONAL = "personal", "Osobní"
    SECRET = "secret", "Tajné"


LEVEL_DESCRIPTIONS = {
    Level.PUBLIC: "Zveřejněno na webu bez přihlášení (akce, příležitosti, "
    "lokality, organizační jednotky).",
    Level.INTERNAL: "Vidí organizátoři a kancelář podle svých oprávnění. "
    "Neobsahuje osobní údaje, přes MCP to vidí každý povolený účet.",
    Level.PERSONAL: "Osobní údaje: jména, kontakty, narozeniny, adresy, "
    "poznámky o lidech. Přes MCP jen účty se smlouvou o zpracování osobních "
    "údajů.",
    Level.SECRET: "Zdravotní údaje a dokumenty plné osobních údajů. MCP je "
    "nevrací nikomu.",
}

UNDOCUMENTED_APPS = {
    "admin",
    "auth",
    "authtoken",
    "contenttypes",
    "cookbook",
    "cookbook_categories",
    "game_book",
    "game_book_categories",
    "gis",
    "login_code",
    "oauth2_provider",
    "sessions",
}
UNDOCUMENTED_MODELS = {"event.EventDraft", "other.DuplicateUser", "other.SavedFile"}
UNDOCUMENTED_FIELDS = {
    "bis.User.password",
    "bis.User.is_bot",
    "bis.User.sees_personal_data_over_mcp",
}

PUBLIC = Level.PUBLIC
INTERNAL = Level.INTERNAL
PERSONAL = Level.PERSONAL
SECRET = Level.SECRET

PUBLISHED_CONTACT = "Zveřejněno na webu jako kontakt."
ANSWER = (
    "Úroveň určuje citlivost otázky: běžná je interní, osobní osobní, "
    "zdravotní tajná. Neklasifikovaná otázka se chová jako tajná."
)

_CATEGORY = {PUBLIC: ["name", "slug"]}

SENSITIVITY = {
    "bis.Location": {
        PUBLIC: [
            "name",
            "description",
            "address",
            "gps_location",
            "program",
            "accessibility_from_prague",
            "accessibility_from_brno",
            "volunteering_work",
            "volunteering_work_done",
            "volunteering_work_goals",
            "options_around",
            "facilities",
            "web",
            "region",
        ],
        INTERNAL: [
            "is_traditional",
            "for_beginners",
            "is_full",
            "is_unexplored",
        ],
    },
    "bis.LocationPhoto": {PUBLIC: ["location", "photo"]},
    "bis.LocationContactPerson": {
        INTERNAL: ["location"],
        PERSONAL: ["first_name", "last_name", "phone", "email"],
    },
    "bis.LocationPatron": {
        INTERNAL: ["location"],
        PERSONAL: ["first_name", "last_name", "phone", "email"],
    },
    "bis.User": {
        INTERNAL: [
            "last_login",
            "subscription_status",
            "health_insurance_company",
            "pronoun",
            "is_active",
            "date_joined",
            "last_after_event_email",
            "is_contact_information_verified",
            "roles",
        ],
        PERSONAL: [
            "first_name",
            "last_name",
            "nickname",
            "birth_name",
            "phone",
            "email",
            "birthday",
            "photo",
            "office_workers_note",
            "vokativ",
        ],
        SECRET: ["health_issues", "behaviour_issues"],
    },
    "bis.UserEmail": {INTERNAL: ["user", "order"], PERSONAL: ["email"]},
    "bis.UserAddress": {
        INTERNAL: ["region", "user"],
        PERSONAL: ["street", "city", "zip_code"],
    },
    "bis.UserContactAddress": {
        INTERNAL: ["region", "user"],
        PERSONAL: ["street", "city", "zip_code"],
    },
    "bis.UserClosePerson": {
        INTERNAL: ["user"],
        PERSONAL: ["first_name", "last_name", "phone", "email"],
    },
    "bis.EYCACard": {
        INTERNAL: ["user", "submitted_for_creation", "sent_to_user", "valid_till"],
        PERSONAL: ["number"],
    },
    "bis.Membership": {
        INTERNAL: [
            "user",
            "category",
            "administration_unit",
            "year",
        ],
    },
    "bis.Qualification": {
        INTERNAL: [
            "user",
            "category",
            "valid_since",
            "valid_till",
            "approved_by",
        ],
    },
    "bis.QualificationNote": {
        INTERNAL: ["user", "created_by", "created_at"],
        PERSONAL: ["education_members_note"],
    },
    "bis.Event": {
        PUBLIC: [
            "name",
            "start",
            "start_time",
            "end",
            "duration",
            "location",
            "group",
            "category",
            "program",
            "intended_for",
            "tags",
            "administration_units",
        ],
        INTERNAL: [
            "is_canceled",
            "is_closed",
            "is_archived",
            "number_of_sub_events",
            "online_link",
            "uid",
            "shared_folder_url",
            "main_organizer",
            "other_organizers",
            "created_by",
            "created_at",
            "closed_at",
            "is_attendance_list_required",
        ],
        PERSONAL: ["organizers_note"],
    },
    "categories.GrantCategory": _CATEGORY,
    "categories.EventIntendedForCategory": _CATEGORY,
    "categories.DietCategory": _CATEGORY,
    "categories.QualificationCategory": {
        PUBLIC: ["name", "slug", "parents", "can_approve"]
    },
    "categories.AdministrationUnitCategory": _CATEGORY,
    "categories.MembershipCategory": _CATEGORY,
    "categories.EventGroupCategory": _CATEGORY,
    "categories.EventCategory": {
        PUBLIC: ["name", "description", "slug", "order", "is_active"]
    },
    "categories.EventTag": {PUBLIC: ["name", "slug", "description", "is_active"]},
    "categories.EventProgramCategory": {PUBLIC: ["name", "slug", "email"]},
    "categories.DonationSourceCategory": {INTERNAL: ["name", "slug"]},
    "categories.OrganizerRoleCategory": _CATEGORY,
    "categories.TeamRoleCategory": _CATEGORY,
    "categories.OpportunityCategory": {PUBLIC: ["name", "description", "slug"]},
    "categories.OpportunityPriority": _CATEGORY,
    "categories.LocationProgramCategory": _CATEGORY,
    "categories.LocationAccessibilityCategory": _CATEGORY,
    "categories.RoleCategory": _CATEGORY,
    "categories.HealthInsuranceCompany": _CATEGORY,
    "categories.PronounCategory": _CATEGORY,
    "categories.DonorEventCategory": {INTERNAL: ["description", "slug"]},
    "questionnaire.EventApplication": {
        INTERNAL: [
            "event_registration",
            "user",
            "state",
            "is_child_application",
            "pronoun",
            "created_at",
            "paid_for",
        ],
        PERSONAL: [
            "first_name",
            "last_name",
            "nickname",
            "phone",
            "email",
            "birthday",
            "applicant_note",
        ],
        SECRET: ["health_issues"],
    },
    "questionnaire.EventApplicationClosePerson": {
        INTERNAL: ["application"],
        PERSONAL: ["first_name", "last_name", "phone", "email"],
    },
    "questionnaire.EventApplicationAddress": {
        INTERNAL: ["region", "application"],
        PERSONAL: ["street", "city", "zip_code"],
    },
    "questionnaire.Questionnaire": {
        PUBLIC: ["event_registration", "introduction", "after_submit_text"]
    },
    "questionnaire.Question": {
        PUBLIC: ["question", "data", "is_required", "order", "questionnaire"],
        INTERNAL: ["sensitivity"],
    },
    "questionnaire.Answer": {
        INTERNAL: ["question", "application"],
        SECRET: ["answer", "data"],
    },
    "feedback.EventFeedback": {
        INTERNAL: ["event", "user", "created_at"],
        PERSONAL: ["name", "email"],
    },
    "feedback.FeedbackForm": {
        PUBLIC: ["event", "introduction", "after_submit_text"],
        INTERNAL: ["email_subject", "email_content", "sent_at"],
    },
    "feedback.Inquiry": {
        PUBLIC: ["inquiry", "slug", "data", "is_required", "order", "feedback_form"],
        INTERNAL: ["sensitivity"],
    },
    "feedback.Reply": {
        INTERNAL: ["inquiry", "feedback"],
        SECRET: ["reply", "value", "data"],
    },
    "event.EventFinance": {
        INTERNAL: [
            "event",
            "grant_category",
            "grant_amount",
            "total_event_cost",
            "budget",
        ],
        PERSONAL: ["bank_account_number"],
    },
    "event.EventFinanceReceipt": {INTERNAL: ["finance"], PERSONAL: ["receipt"]},
    "event.EventPropagation": {
        PUBLIC: [
            "event",
            "minimum_age",
            "maximum_age",
            "cost",
            "accommodation",
            "working_hours",
            "working_days",
            "web_url",
            "invitation_text_introduction",
            "invitation_text_practical_information",
            "invitation_text_work_description",
            "invitation_text_about_us",
            "diets",
        ],
        INTERNAL: ["is_shown_on_web"],
        PERSONAL: ["organizers", "contact_name", "contact_phone", "contact_email"],
    },
    "event.VIPEventPropagation": {
        INTERNAL: [
            "event",
            "goals_of_event",
            "program",
            "short_invitation_text",
            "rover_propagation",
        ],
    },
    "event.EventRegistration": {
        PUBLIC: [
            "event",
            "is_registration_required",
            "alternative_registration_link",
            "is_event_full",
        ],
    },
    "event.EventRecord": {
        INTERNAL: [
            "event",
            "total_hours_worked",
            "comment_on_work_done",
            "number_of_participants",
            "number_of_participants_under_26",
            "attendance_list_type",
            "is_event_closed_email_enabled",
            "participants",
        ],
    },
    "event.EventPropagationImage": {PUBLIC: ["propagation", "order", "image"]},
    "event.EventAttendanceListPage": {
        INTERNAL: ["record", "created_at"],
        SECRET: ["page"],
    },
    "event.EventPhoto": {INTERNAL: ["record", "created_at"], PERSONAL: ["photo"]},
    "other.UserTag": {INTERNAL: ["name", "expires_at", "users"]},
    "other.Announcement": {INTERNAL: ["text", "severity", "start", "end", "for_roles"]},
    "other.DashboardItem": {
        INTERNAL: [
            "date",
            "visible_date",
            "name",
            "description",
            "repeats_every_year",
            "for_roles",
        ],
    },
    "other.DonationPointsAggregation": {INTERNAL: ["name", "slug", "description"]},
    "other.DonationPoints": {INTERNAL: ["name", "since", "till", "file"]},
    "other.DonationPointsSection": {INTERNAL: ["donation_points"]},
    "other.DonationPointsColumn": {
        INTERNAL: ["aggregation", "points_per_each", "section"]
    },
    "donations.Donor": {
        INTERNAL: [
            "user",
            "subscribed_to_newsletter",
            "is_public",
            "do_not_call",
            "do_not_solicit",
            "date_joined",
            "regional_center_support",
            "basic_section_support",
        ],
        PERSONAL: ["formal_vokativ", "fundraisers_note"],
    },
    "donations.Company": {INTERNAL: ["donor"], PERSONAL: ["name", "ico", "address"]},
    "donations.VariableSymbol": {INTERNAL: ["donor"], PERSONAL: ["variable_symbol"]},
    "donations.Pledge": {
        INTERNAL: [
            "id",
            "donor",
            "donation_source",
            "is_recurrent",
            "recurrent_state",
            "pledged_at",
        ],
    },
    "donations.FundraisingCampaign": {INTERNAL: ["name", "slug"]},
    "donations.DonorEvent": {
        INTERNAL: [
            "donor",
            "event_type",
            "created_at",
            "campaign",
            "pledge",
            "reminder",
            "created_by",
        ],
        PERSONAL: ["fundraisers_note"],
    },
    "donations.Donation": {
        INTERNAL: [
            "donor",
            "pledge",
            "donated_at",
            "amount",
            "donation_source",
        ],
        PERSONAL: ["info"],
    },
    "donations.UploadBankRecords": {SECRET: ["file"]},
    "administration_units.AdministrationUnit": {
        PUBLIC: [
            "name",
            "abbreviation",
            "description",
            "image",
            "is_for_kids",
            "www",
            "facebook",
            "instagram",
            "ic",
            "bank_account_number",
            "existed_since",
            "existed_till",
            "gps_location",
            "category",
            "chairman",
            "vice_chairman",
            "manager",
            "board_members",
        ],
        INTERNAL: [
            "data_box",
            "custom_statues",
        ],
        PERSONAL: ["phone", "email"],
    },
    "administration_units.AdministrationUnitAddress": {
        PUBLIC: ["street", "city", "zip_code", "region", "administration_unit"]
    },
    "administration_units.AdministrationUnitContactAddress": {
        PUBLIC: ["street", "city", "zip_code", "region", "administration_unit"]
    },
    "administration_units.GeneralMeeting": {
        INTERNAL: ["administration_unit", "date", "place"]
    },
    "administration_units.AdministrationSubUnit": {
        PUBLIC: [
            "administration_unit",
            "name",
            "description",
            "is_for_kids",
            "is_active",
            "www",
            "facebook",
            "instagram",
            "gps_location",
            "main_leader",
            "sub_leaders",
        ],
        PERSONAL: ["phone", "email"],
    },
    "administration_units.AdministrationSubUnitAddress": {
        PUBLIC: ["street", "city", "zip_code", "region", "sub_unit"]
    },
    "administration_units.BrontosaurusMovement": {
        INTERNAL: [
            "director",
            "finance_director",
            "bis_administrators",
            "office_workers",
            "audit_committee",
            "executive_committee",
            "education_members",
            "fundraisers",
        ],
    },
    "ecomail.Contact": {PERSONAL: ["email"]},
    "ecomail.ContactLog": {
        INTERNAL: ["contact", "created", "status"],
        PERSONAL: ["log"],
    },
    "opportunities.Opportunity": {
        PUBLIC: [
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
            "image",
        ],
        INTERNAL: ["contact_person", "created_at"],
        PERSONAL: ["contact_name", "contact_phone", "contact_email"],
    },
    "opportunities.OfferedHelp": {
        INTERNAL: [
            "user",
            "additional_organizer_role",
            "additional_team_role",
            "info",
            "programs",
            "organizer_roles",
            "team_roles",
        ],
    },
    "regions.Region": {PUBLIC: ["name", "area"]},
    "regions.ZipCode": {PUBLIC: ["zip_code", "region"]},
}

NOTES = {
    "bis.LocationPatron.first_name": "Zveřejněno na webu jako patron lokality.",
    "bis.LocationPatron.last_name": "Zveřejněno na webu jako patron lokality.",
    "bis.LocationPatron.phone": "Zveřejněno na webu jako patron lokality.",
    "bis.LocationPatron.email": "Zveřejněno na webu jako patron lokality.",
    "bis.User.first_name": "Organizátorů a vedoucích jednotek zveřejněno na "
    "webu jako kontakt.",
    "bis.User.last_name": "Organizátorů a vedoucích jednotek zveřejněno na "
    "webu jako kontakt.",
    "bis.User.phone": "Organizátorů a vedoucích jednotek zveřejněno na webu "
    "jako kontakt.",
    "bis.User.email": "Organizátorů a vedoucích jednotek zveřejněno na webu "
    "jako kontakt.",
    "bis.User.health_insurance_company": "Jen název pojišťovny, ne zdravotní údaj.",
    "questionnaire.Question.sensitivity": "Běžná / osobní / zdravotní, přiřazuje Groq.",
    "questionnaire.Answer.answer": ANSWER,
    "questionnaire.Answer.data": ANSWER,
    "feedback.Inquiry.sensitivity": "Běžná / osobní / zdravotní, přiřazuje Groq.",
    "feedback.Reply.reply": ANSWER,
    "feedback.Reply.value": ANSWER,
    "feedback.Reply.data": ANSWER,
    "event.EventFinanceReceipt.receipt": "Sken účtenky.",
    "event.EventPropagation.organizers": "Jména organizátorů, zveřejněno na webu.",
    "event.EventPropagation.contact_name": PUBLISHED_CONTACT,
    "event.EventPropagation.contact_phone": PUBLISHED_CONTACT,
    "event.EventPropagation.contact_email": PUBLISHED_CONTACT,
    "event.EventAttendanceListPage.page": "Sken prezenční listiny se jmény a podpisy.",
    "event.EventPhoto.photo": "Fotky lidí z akce.",
    "donations.UploadBankRecords.file": "Bankovní výpis.",
    "donations.Company.ico": "U podnikající fyzické osoby jde o osobní údaj.",
    "donations.VariableSymbol.variable_symbol": "Identifikuje dárce v bance.",
    "administration_units.AdministrationUnit.phone": PUBLISHED_CONTACT,
    "administration_units.AdministrationUnit.email": PUBLISHED_CONTACT,
    "administration_units.AdministrationSubUnit.phone": PUBLISHED_CONTACT,
    "administration_units.AdministrationSubUnit.email": PUBLISHED_CONTACT,
    "opportunities.Opportunity.contact_name": PUBLISHED_CONTACT,
    "opportunities.Opportunity.contact_phone": PUBLISHED_CONTACT,
    "opportunities.Opportunity.contact_email": PUBLISHED_CONTACT,
    "opportunities.OfferedHelp.info": "Co člověk nabízí, volný text.",
    "ecomail.ContactLog.log": "Historie e-mailové komunikace s kontaktem.",
}


def model_fields(model):
    return [
        field
        for field in model._meta.get_fields()
        if (field.concrete or field.many_to_many)
        and not field.auto_created
        and not field.name.startswith("_")
        and f"{model._meta.label}.{field.name}" not in UNDOCUMENTED_FIELDS
    ]


def documented_models():
    return [
        model
        for model in apps.get_models()
        if model._meta.app_label not in UNDOCUMENTED_APPS
        and model._meta.label not in UNDOCUMENTED_MODELS
        and not model._meta.proxy
    ]


def level_of(model, name):
    for level, names in SENSITIVITY[model._meta.label].items():
        if name in names:
            return level
    raise KeyError(f"{model._meta.label}.{name} has no sensitivity level")


def overview():
    """Rows for the /docs/ page, one per model."""
    models = documented_models()
    return [
        {
            "app": model._meta.app_config.verbose_name,
            "model": model._meta.label,
            "name": str(model._meta.verbose_name),
            "fields": [
                {
                    "name": field.name,
                    "label": str(getattr(field, "verbose_name", field.name)),
                    "level": level_of(model, field.name),
                    "note": NOTES.get(f"{model._meta.label}.{field.name}", ""),
                    "target": field.related_model._meta.label
                    if field.related_model in models
                    else None,
                }
                for field in model_fields(model)
            ],
        }
        for model in models
    ]
