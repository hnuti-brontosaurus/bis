import logging

from django.conf import settings
from vokativ import vokativ

from categories.models import PronounCategory
from ecomail import ecomail
from project.settings import EMAIL

SENDER_NAME = 'BIS'


def password_reset_link(user, email, login_code):
    ecomail.send_email(
        EMAIL, SENDER_NAME,
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
        EMAIL, SENDER_NAME,
        "Potvrzení přihlášení na akci", template,
        [email],
        variables=variables
    )
    email = event.propagation.contact_email or event.main_organizer.email
    if not email:
        logging.error("Organizer does not have an email")
        return

    ecomail.send_email(
        EMAIL, SENDER_NAME,
        "Nová přihláška!", "148",
        [email],
        variables={
            "participant_name": application.nickname or f"{application.first_name} {application.last_name}",
            'event_name': event.name,
            "event_applications_link": f"{settings.FULL_HOSTNAME}/org/akce/{event.id}/prihlasky"
        }
    )


def event_created(event):
    return



def login_code(email, code):
    text(email, 'Kód pro přihlášení', f'tvůj kód pro přihlášení je {code}.')


def text(email, subject, text, reply_to=None):
    text = text.replace("\n", "<br>")
    ecomail.send_email(
        EMAIL, SENDER_NAME,
        subject,
        '111',
        [email],
        reply_to=reply_to,
        variables={'content': text}
    )
