from base64 import b64encode
from collections import defaultdict
from datetime import date, timedelta, timezone

from dateutil.utils import today
from django.conf import settings
from vokativ import vokativ

from administration_units.models import AdministrationUnit
from bis.helpers import make_a, make_ul
from bis.models import Qualification
from categories.models import EventProgramCategory, PronounCategory
from common.helpers import get_date_range
from ecomail import ecomail
from event.models import Event
from feedback.models import Reply
from opportunities.models import Opportunity

emails = {
    "bis": ("BIS", "bis@brontosaurus.cz"),
    "movement": ("Hnutí Brontosaurus", "hnuti@brontosaurus.cz"),
    "education": ("Vzdělávání", "vzdelavani@brontosaurus.cz"),
    "volunteering": ("Dobrovolnictví", "dobrovolnictvi@brontosaurus.cz"),
    "donation": ("Dárcovství", "darcovstvi@brontosaurus.cz"),
}


def login_code(email, code):
    text([email], "Kód pro přihlášení", f"tvůj kód pro přihlášení je {code}.")


def text(recipients, subject, content, reply_to=None, attachments=None):
    content = content.replace("\n", "<br>")
    ecomail.send_email(
        emails["bis"],
        111,
        recipients,
        subject=subject,
        reply_to=reply_to,
        variables={"content": content},
        attachments=attachments,
    )


def password_reset_link(user, email, login_code):
    ecomail.send_email(
        emails["bis"],
        151,
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
    contact_email = event.propagation.contact_email or event.main_organizer.email
    variables = {
        "event_name": event.name,
        "event_date": event.get_date(),
        "contact_email": contact_email,
    }
    if application.is_child_application:
        template = 182
        email = application.close_person.email
        variables["child_name"] = application.first_name

    else:
        template = 147
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
        template,
        [email],
        reply_to=[contact_email],
        variables=variables,
    )

    ecomail.send_email(
        emails["bis"],
        148,
        [contact_email],
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
        142,
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
        150,
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
            153,
            [program.email],
            variables={
                "new_events": events_to_list(new_events),
                "closed_events": events_to_list(closed_events),
                "unclosed_events": events_to_list(unclosed_events),
            },
        )


def event_not_closed_10_days():
    for event in get_unclosed_events().filter(
        end=date.today() - timedelta(days=10),
    ):
        organizers = event.other_organizers.all()
        ecomail.send_email(
            emails["bis"],
            209,
            [organizer.email for organizer in organizers if organizer.email],
            variables={
                "vokativs": ", ".join(organizer.vokativ for organizer in organizers),
                "event_name": event.name,
                "program_email": event.program.email,
                "bis_link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}/uzavrit",
            },
        )


def event_not_closed_20_days():
    for event in get_unclosed_events().filter(
        end__in=[date.today() - timedelta(days=20 + 10 * i) for i in range(3 * 12)],
    ):
        if not event.main_organizer:
            continue

        ecomail.send_email(
            emails["bis"],
            163,
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
            169,
            [participant.email],
            variables={
                "vokativ": participant.vokativ,
                "event_name": event.name,
            },
        )
    participants_to_notify.update(last_after_event_email=date.today())


def event_attendance_or_photos_notification(event):
    ecomail.send_email(
        emails["bis"],
        225,
        [event.program.email],
        variables={"event": event.name},
    )


def get_consultants():
    valid_qualifications = Qualification.objects.filter(
        valid_since__lte=date.today(),
        valid_till__gte=date.today(),
    )
    return {
        "consultants": make_ul(
            qualification.user.get_proper_name()
            for qualification in valid_qualifications.filter(
                category__slug="consultant"
            )
        ),
        "kids_consultants": make_ul(
            qualification.user.get_proper_name()
            for qualification in valid_qualifications.filter(
                category__slug="consultant_for_kids"
            )
        ),
    }


def qualification_about_to_end():
    to_date = date.today() + timedelta(days=90)
    for qualification in Qualification.get_expiring_qualifications(
        to_date, Qualification.objects.filter(valid_till=to_date)
    ):
        if qualification.category.slug in [
            "consultant",
            "instructor",
            "consultant_for_kids",
            "organizer_without_education",
        ]:
            continue

        ecomail.send_email(
            emails["education"],
            155,
            [qualification.user.email],
            variables={
                "vokativ": qualification.user.vokativ,
                "qualification": qualification.category.name,
                **get_consultants(),
            },
        )


def qualification_ends_this_year() -> None:
    """
    Send mail to education with lists of consultants, instructors and BRĎO consultants
    whose qualifications end this year.
    (email 8a)
    """
    year = date.today().year
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    qualifications = Qualification.objects.filter(
        valid_till__gte=start,
        valid_till__lte=end,
        category__slug__in=["consultant", "consultant_for_kids", "instructor"],
    )

    categories = defaultdict(list)
    for qualification in Qualification.get_expiring_qualifications(end, qualifications):
        categories[qualification.category.slug].append(qualification.user)

    categories = {
        slug: make_ul(user.get_proper_name() for user in users)
        for slug, users in categories.items()
    }

    ecomail.send_email(
        emails["bis"],
        255,
        [emails["education"][1]],
        variables={"year": year, **categories},
    )


def qualification_ended():
    for qualification in Qualification.get_expiring_qualifications(
        date.today(), Qualification.objects.filter(valid_till=date.today())
    ):
        if qualification.category.slug in [
            "consultant",
            "instructor",
            "consultant_for_kids",
            "organizer_without_education",
        ]:
            continue

        ecomail.send_email(
            emails["education"],
            156,
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
        157,
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
    recipient_email = opportunity.contact_email or opportunity.contact_person.email
    created_by_email = opportunity.contact_person.email
    ecomail.send_email(
        emails["volunteering"],
        145,
        [recipient_email],
        reply_to=[created_by_email],
        variables={
            "created_by": opportunity.contact_person.get_name(),
            "opportunity": opportunity.name,
            "created_by_email": created_by_email,
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
        146,
        [emails["volunteering"][1]],
        variables={"opportunities": f"<ul>{opportunities}</ul>"},
    )


def fill_memberships(call):
    template_ids = {
        1: 159,
        2: 160,
    }

    for administration_unit in AdministrationUnit.objects.all():
        if not administration_unit.is_active():
            continue

        ecomail.send_email(
            emails["bis"],
            template_ids[call],
            [administration_unit.chairman.email],
            reply_to=[emails["movement"][1]],
            variables={
                "vokativ": administration_unit.chairman.vokativ,
                "administration_unit": administration_unit.abbreviation,
            },
        )


def donation_confirmation(donor, confirmation, year):
    ecomail.send_email(
        emails["donation"],
        167,
        [donor.user.email],
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
    opportunities = [
        {
            "name": opportunity.name,
            "link": f"https://brontosaurus.cz/zapoj-se/prilezitost/{opportunity.id}/",
            "location": opportunity.location.name,
            "when": get_date_range(opportunity.start, opportunity.end),
        }
        for opportunity in opportunities
    ]
    ecomail.send_email(
        emails["education"],
        201,
        ["organizatori@brontosaurus.cz"],
        variables={"opportunities": opportunities},
    )


def feedback_created(feedback):
    event = feedback.event
    ecomail.send_email(
        emails["bis"],
        248,
        [event.main_organizer.email],
        variables={
            "participant_name": feedback.name or "neznámý účastník",
            "event_name": event.name,
            "event_feedbacks_link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}/zpetna_vazba",
        },
    )


def send_feedback_request(event):
    if not hasattr(event, "record"):
        return

    for participant in event.record.participants.all():
        ecomail.send_email(
            emails["bis"],
            305,
            [participant.email],
            variables={
                "event_name": event.name,
                "event_date": event.get_date(),
                "vokativ": participant.vokativ,
                "feedback_link": f"{settings.FULL_HOSTNAME}/akce/{event.id}/zpetna_vazba",
            },
        )


def send_automatic_feedback():
    for event in Event.objects.filter(
        end=date.today() - timedelta(days=20),
        feedback_form__sent_at__isnull=True,
        feedback_form__isnull=False,
        program__slug__in=[
            "nature",
            "monuments",
            "holidays_with_brontosaurus",
            "education",
            "none",
        ],
        group__slug__in=["camp", "weekend_event"],
    ).exclude(
        intended_for__slug="for_kids",
    ):
        send_feedback_request(event)
        event.feedback_form.sent_at = date.today()
        event.feedback_form.save()


def expressed_engagement_in_feedback():
    """
    Email hnuti with info about people who filled in the feedback form
    that they want to participate more in HB (in the 7 days).
    - Missing name/email are replaced with defaults.
    - Email is sent even if it is empty.
    (email 36)
    """
    replies = Reply.objects.select_related("feedback", "feedback__event").filter(
        feedback__created_at__gte=date.today() - timedelta(days=7),
        inquiry__slug="involvement_means",
    )

    items = (
        ", ".join(
            (
                reply.feedback.name or "jméno nevyplněno",
                f"email: {reply.feedback.email or 'email nevyplněn'}",
                f"akce: {reply.feedback.event.name}",
                f"jak se chce zapojit: {reply.reply}",
            )
        )
        for reply in replies
        if "nechci" not in reply.reply
    )

    ecomail.send_email(
        emails["bis"],
        312,
        [emails["movement"][1]],
        variables={"replies": make_ul(items)},
    )
