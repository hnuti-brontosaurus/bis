import logging
from datetime import date, timedelta

from django.conf import settings
from vokativ import vokativ

from categories.models import PronounCategory, EventProgramCategory
from ecomail import ecomail
from event.models import Event

emails = {
    'bis': ('BIS', 'bis@brontosaurus.cz'),
    'movement': ('Hnutí Brontosaurus', 'hnuti@brontosaurus.cz'),
}


def password_reset_link(user, email, login_code):
    ecomail.send_email(
        emails['bis'],
        "Obnova hesla",
        "151",
        [email],
        variables={"link": f'{settings.FULL_HOSTNAME}/reset_password'
                           f'?email={email}'
                           f'&code={login_code.code}'
                           f'&password_exists={user.has_usable_password()}'}
    )


def application_created(application):
    event = application.event_registration.event
    variables = {
        'event_name': event.name,
        'event_date': event.get_date()
    }
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
                'vokativ': application.user.vokativ
            }
        else:
            variables['vokativ'] = (
                    vokativ(application.nickname).capitalize() or
                    vokativ(application.first_name.split(' ')[0]).capitalize()
            )

    ecomail.send_email(
        emails['bis'],
        "Potvrzení přihlášení na akci", template,
        [email],
        variables=variables
    )
    email = event.propagation.contact_email or event.main_organizer.email
    if not email:
        logging.error("Organizer does not have an email")
        return

    ecomail.send_email(
        emails['bis'],
        "Nová přihláška!", "148",
        [email],
        variables={
            "participant_name": application.nickname or f"{application.first_name} {application.last_name}",
            'event_name': event.name,
            "event_applications_link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}/prihlasky"
        }
    )


def event_created(event):
    ecomail.send_email(
        emails['bis'],
        "Akce je zadána v BIS", "142",
        [event.main_organizer.email],
        variables={
            'created_by': event.created_by.get_name(),
            'vokativ': event.created_by.vokativ,
            'created_by_email': event.created_by.email,
            'event_name': event.name,
            'link': f'{settings.FULL_HOSTNAME}/org/akce/{event.id}',
        }
    )


def events_created_summary():
    for program in EventProgramCategory.objects.exclude(slug='none'):
        events = Event.objects.filter(
            is_canceled=False,
            created_at__gte=date.today() - timedelta(days=7),
            program__slug__in=[program.slug, 'none']
        )
        if not events.count():
            continue

        events = "".join(f"<li>{event.name}, {event.get_date()}, Program: {program.name}</li>" for event in events)
        ecomail.send_email(
            emails['bis'],
            "Seznam zadaných akcí koordinátorovi",
            "153",
            [program.email],
            variables={
                'events': f'<ul>{events}</ul>'
            }
        )


def event_ended_notify_organizers():
    for event in Event.objects.filter(
            is_canceled=False,
            end=date.today() - timedelta(days=2),
    ):
        organizers = event.other_organizers.all()
        ecomail.send_email(
            emails['bis'], "Organizátorům po akci", "161",
            [organizer.email for organizer in organizers if organizer.email],
            variables={
                'vokativs': ", ".join(organizer.vokativ for organizer in organizers),
                'event_name': event.name,
                'program_email': event.program.email,
            }
        )


def event_not_closed_10_days():
    for event in Event.objects.filter(
            is_canceled=False,
            is_complete=False,
            is_closed=False,
            end=date.today() - timedelta(days=10),
    ):
        ecomail.send_email(
            emails['bis'], "Blížící se termín uzavření akce", "162",
            [event.main_organizer.email],
            variables={
                **PronounCategory.get_variables(event.main_organizer),
                'main_organizer_name': event.main_organizer.vokativ,
                'event_name': event.name,
                'program_email': event.program.email,
            }
        )


def event_not_closed_20_days():
    for event in Event.objects.filter(
            is_canceled=False,
            is_complete=False,
            is_closed=False,
            end__in=[date.today() - timedelta(days=20 + 10 * i) for i in range(3 * 12)],
    ):
        ecomail.send_email(
            emails['bis'], "Akce je po termínu pro její uzavření", "163",
            [event.main_organizer.email],
            variables={
                **PronounCategory.get_variables(event.main_organizer),
                'main_organizer_name': event.main_organizer.vokativ,
                'event_name': event.name,
                'program_email': event.program.email,
            }
        )

def event_end_participants_notification():
    for event in Event.objects.filter(
        is_canceled=False,
        end=date.today() - timedelta(days=10)
    ):
        if not hasattr(event, 'record'):
            continue

        for participant in event.record.participants.all():
            if not participant.email:
                continue

            ecomail.send_email(
                emails['movement'], "Děkujeme za účast na akci Hnutí", "169",
                [participant.email],
                variables={
                    'vokativ': participant.vokativ,
                    'event_name': event.name,
                }
            )

def notify_not_closed_events_summary():
    for program in EventProgramCategory.objects.exclude(slug='none'):
        events = Event.objects.filter(
            is_canceled=False,
            is_completed=False,
            is_closed=False,
            end__lte=date.today() - timedelta(days=20),
            program__slug__in=[program.slug, 'none']
        )
        if not events.count():
            continue

        events = "".join(f"<li>{event.name}, {event.get_date()}, Program: {program.name}</li>" for event in events)
        ecomail.send_email(
            emails['bis'],
            "Seznam neuzavřených akcí",
            "154",
            [program.email],
            variables={
                'events': f'<ul>{events}</ul>'
            }
        )


def login_code(email, code):
    text(email, 'Kód pro přihlášení', f'tvůj kód pro přihlášení je {code}.')


def text(email, subject, text, reply_to=None):
    text = text.replace("\n", "<br>")
    ecomail.send_email(
        emails['bis'],
        subject,
        '111',
        [email],
        reply_to=reply_to,
        variables={'content': text}
    )

