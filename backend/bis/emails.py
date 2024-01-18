from base64 import b64encode
from datetime import date, timedelta

from administration_units.models import AdministrationUnit
from bis.helpers import make_a, make_ul
from bis.models import Qualification
from categories.models import EventProgramCategory, PronounCategory
from dateutil.utils import today
from django.conf import settings
from django.utils.formats import date_format
from ecomail import ecomail
from event.models import Event
from opportunities.models import Opportunity
from vokativ import vokativ

emails = {
    "bis": ("BIS", "bis@brontosaurus.cz"),
    "movement": ("Hnutí Brontosaurus", "hnuti@brontosaurus.cz"),
    "education": ("Vzdělávání", "vzdelavani@brontosaurus.cz"),
    "volunteering": ("Dobrovolnictví", "dobrovolnictvi@brontosaurus.cz"),
    "adoption": ("Adopce Brontosaura", "adopce@brontosaurus.cz"),
}


def login_code(email, code):
    text(email, "Kód pro přihlášení", f"tvůj kód pro přihlášení je {code}.")


def text(email, subject, text, reply_to=None):
    text = text.replace("\n", "<br>")
    ecomail.send_email(
        emails["bis"],
        subject,
        "111",
        [email],
        reply_to=reply_to,
        variables={"content": text},
    )


def password_reset_link(user, email, login_code):
    ecomail.send_email(
        emails["bis"],
        "Obnova hesla",
        "151",
        [email],
        variables={
            "link": f"{settings.FULL_HOSTNAME}/reset_password"
            f"?email={email}"
            f"&code={login_code.code}"
            f"&password_exists={user.has_usable_password()}"
        },
    )


def application_created(application):
    event = application.event_registration.event
    variables = {"event_name": event.name, "event_date": event.get_date()}
    if application.is_child_application:
        template = "182"
        email = application.close_person.email
        variables["child_name"] = application.first_name

    else:
        template = "147"
        email = application.email
        if application.user:
            variables |= {
                **PronounCategory.get_variables(application.user),
                "vokativ": application.user.vokativ,
            }
        else:
            variables["vokativ"] = (
                vokativ(application.nickname).capitalize()
                or vokativ(application.first_name.split(" ")[0]).capitalize()
            )

    ecomail.send_email(
        emails["bis"],
        "Potvrzení přihlášení na akci",
        template,
        [email],
        variables=variables,
    )
    email = event.propagation.contact_email or event.main_organizer.email
    ecomail.send_email(
        emails["bis"],
        "Nová přihláška!",
        "148",
        [email],
        variables={
            "participant_name": application.nickname
            or f"{application.first_name} {application.last_name}",
            "event_name": event.name,
            "event_applications_link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}/prihlasky",
        },
    )


def event_created(event):
    ecomail.send_email(
        emails["bis"],
        "Akce je zadána v BIS",
        "142",
        [event.main_organizer.email],
        variables={
            "created_by": event.created_by.get_name(),
            "vokativ": event.created_by.vokativ,
            "created_by_email": event.created_by.email,
            "event_name": event.name,
            "link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}",
        },
    )

    recipients = [
        (au.email or au.chairman.email) for au in event.administration_units.all()
    ]
    recipients = [email for email in recipients if email != event.main_organizer.email]
    ecomail.send_email(
        emails["bis"],
        "Informace, že někdo založil akci pod mým ZČ",
        "150",
        recipients,
        variables={
            "event_name": event.name,
            "event_date": event.get_date(),
            "main_organizer": event.main_organizer.get_name(),
            "main_organizer_email": event.main_organizer.email,
            "bis_link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}",
            "backend_link": f"{settings.FULL_HOSTNAME}/admin/bis/event/{event.id}/change/",
        },
    )


def get_unclosed_events():
    return (
        Event.objects.exclude(is_canceled=True)
        .exclude(is_closed=True)
        .exclude(is_archived=True)
    )


def events_to_list(events):
    return make_ul(
        f"{event.name}, {event.get_date()}, "
        + make_a("BIS", f"{settings.FULL_HOSTNAME}/org/akce/{event.id}")
        + ", "
        + make_a("Administrace", f"{settings.FULL_HOSTNAME}/admin/bis/event/{event.id}")
        for event in events
    )


def events_summary():
    for program in EventProgramCategory.objects.all():
        new_events = Event.objects.filter(
            is_canceled=False,
            created_at__gte=date.today() - timedelta(days=7),
            program__slug=program.slug,
        )

        closed_events = Event.objects.filter(
            closed_at__gte=date.today() - timedelta(days=7), program__slug=program.slug
        )

        unclosed_events = get_unclosed_events().filter(
            end__lte=date.today() - timedelta(days=20), program__slug=program.slug
        )

        ecomail.send_email(
            emails["bis"],
            "Seznam zadaných akcí koordinátorovi",
            "153",
            [program.email],
            variables={
                "new_events": events_to_list(new_events),
                "closed_events": events_to_list(closed_events),
                "unclosed_events": events_to_list(unclosed_events),
            },
        )


def event_ended_notify_organizers():
    for event in Event.objects.filter(
        is_canceled=False,
        end=date.today() - timedelta(days=2),
    ):
        organizers = event.other_organizers.all()
        ecomail.send_email(
            emails["bis"],
            "Organizátorům po akci",
            "161",
            [organizer.email for organizer in organizers if organizer.email],
            variables={
                "vokativs": ", ".join(organizer.vokativ for organizer in organizers),
                "event_name": event.name,
                "program_email": event.program.email,
            },
        )


def event_not_closed_10_days():
    for event in get_unclosed_events().filter(
        end=date.today() - timedelta(days=10),
    ):
        ecomail.send_email(
            emails["bis"],
            "Blížící se termín uzavření akce",
            "162",
            [event.main_organizer.email],
            variables={
                **PronounCategory.get_variables(event.main_organizer),
                "main_organizer_name": event.main_organizer.vokativ,
                "event_name": event.name,
                "program_email": event.program.email,
                "bis_link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}/uzavrit",
            },
        )


def event_not_closed_20_days():
    for event in (
        get_unclosed_events()
        .filter(
            end__in=[date.today() - timedelta(days=20 + 10 * i) for i in range(3 * 12)],
        )
        .filter(
            end__gte=date(
                2023, 11, 1
            )  # remove notification for old events, can be removed after 3.1.2024
        )
    ):
        if not event.main_organizer:
            continue

        ecomail.send_email(
            emails["bis"],
            "Akce je po termínu pro její uzavření",
            "163",
            [event.main_organizer.email],
            variables={
                **PronounCategory.get_variables(event.main_organizer),
                "main_organizer_name": event.main_organizer.vokativ,
                "event_name": event.name,
                "program_email": event.program.email,
                "bis_link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}/uzavrit",
            },
        )


def event_end_participants_notification(event):
    if not hasattr(event, "record"):
        return

    if event.end < (date.today() - timedelta(days=60)):
        return

    participants_to_notify = event.record.participants.exclude(
        last_after_event_email__gte=date.today() - timedelta(days=6 * 30)
    )
    for participant in event.record.participants.exclude(
        last_after_event_email__gte=date.today() - timedelta(days=6 * 30)
    ):
        ecomail.send_email(
            emails["movement"],
            "Děkujeme za účast na akci Hnutí",
            "169",
            [participant.email],
            variables={
                "vokativ": participant.vokativ,
                "event_name": event.name,
            },
        )
    participants_to_notify.update(last_after_event_email=date.today())


def get_consultants():
    valid_qualifications = Qualification.objects.filter(
        valid_since__lte=date.today(),
        valid_till__gte=date.today(),
    )
    consultants = [
        qualification.user
        for qualification in valid_qualifications.filter(category__slug="consultant")
    ]
    kids_consultants = [
        qualification.user
        for qualification in valid_qualifications.filter(
            category__slug="consultant_for_kids"
        )
    ]
    consultants = "".join(
        f"<li>{consultant.get_name()}, {consultant.email}</li>"
        for consultant in consultants
    )
    kids_consultants = "".join(
        f"<li>{consultant.get_name()}, {consultant.email}</li>"
        for consultant in kids_consultants
    )

    return {
        "consultants": f"<ul>{consultants}</ul>",
        "kids_consultants": f"<ul>{kids_consultants}</ul>",
    }


def qualification_about_to_end():
    for qualification in Qualification.get_expiring_qualifications(
        date.today() + timedelta(days=90)
    ):
        ecomail.send_email(
            emails["education"],
            "Blíží se konec platnosti kvalifikace",
            "155",
            [qualification.user.email],
            variables={
                "vokativ": qualification.user.vokativ,
                "qualification": qualification.category.name,
                **get_consultants(),
            },
        )


def qualification_ended():
    for qualification in Qualification.get_expiring_qualifications(date.today()):
        ecomail.send_email(
            emails["education"],
            "Konec platnosti kvalifikace",
            "156",
            [qualification.user.email],
            variables={
                "vokativ": qualification.user.vokativ,
                "qualification": qualification.category.name,
                **get_consultants(),
            },
        )


def qualification_created(qualification: Qualification):
    ecomail.send_email(
        emails["education"],
        "Udělení nové kvalifikace",
        "157",
        [qualification.user.email],
        variables={
            "consultant": qualification.approved_by.get_name(),
            "consultant_email": qualification.approved_by.email,
            "qualification": qualification.category.name,
            "valid_till": str(qualification.valid_till),
            **get_consultants(),
        },
    )


def opportunity_created(opportunity: Opportunity):
    email = opportunity.contact_email or opportunity.contact_person.email
    ecomail.send_email(
        emails["volunteering"],
        "Příležitost je zadána v BISu",
        "145",
        [email],
        variables={
            "created_by": opportunity.contact_person.get_name(),
            "opportunity": opportunity.name,
            "created_by_email": opportunity.contact_person.email,
        },
    )


def opportunities_created_summary():
    opportunities = Opportunity.objects.filter(
        created_at__gte=date.today() - timedelta(days=7)
    )
    opportunities = "".join(
        f"<li>{opportunity.name}, {opportunity.category.name}</li>"
        for opportunity in opportunities
    )
    ecomail.send_email(
        emails["bis"],
        "Seznam zadaných příležitostí",
        "146",
        [emails["volunteering"][1]],
        variables={"opportunities": f"<ul>{opportunities}</ul>"},
    )


def fill_memberships(call):
    template_ids = {
        1: "159",
        2: "160",
    }
    subjects = {
        1: "Blížící se termín zadání členů HB do BIS",
        2: "Blížící se termín zadání členů HB do BIS (2.výzva)",
    }

    for administration_unit in AdministrationUnit.objects.all():
        if not administration_unit.is_active():
            continue

        ecomail.send_email(
            emails["bis"],
            subjects[call],
            template_ids[call],
            [administration_unit.chairman.email],
            variables={
                "vokativ": administration_unit.chairman.vokativ,
                "administration_unit": administration_unit.abbreviation,
            },
        )


def donation_confirmation(donor, confirmation, year):
    ecomail.send_email(
        emails["adoption"],
        "Poděkování a potvrzení o daru HB",
        "167",
        ["adopce@brontosaurus.cz"],
        variables={
            "formal_vokativ": donor.formal_vokativ,
            **PronounCategory.get_variables(donor.user),
        },
        attachments=[
            {
                "content_type": "pdf",
                "name": f"Potvrzení o daru, {donor.user.last_name} {year}.pdf",
                "data": b64encode(confirmation.read()).decode(),
            }
        ],
    )


def send_opportunities_summary():
    opportunities = Opportunity.objects.filter(
        on_web_start__lte=today(),
        on_web_end__gte=today(),
    )
    opportunities = make_ul(
        make_a(
            opportunity.name,
            f"https://brontosaurus.cz/zapoj-se/prilezitost/{opportunity.id}/",
        )
        + f", {opportunity.location}, {date_format(opportunity.start)} - {date_format(opportunity.end)}"
        for opportunity in opportunities
    )
    ecomail.send_email(
        emails["bis"],
        "Příležitosti",
        "201",
        # ["organizatori@brontosaurus.cz"],
        ["lamanchy@gmail.com"],
        variables={"opportunities": opportunities},
    )


def feedback_created(instance):
    return None
