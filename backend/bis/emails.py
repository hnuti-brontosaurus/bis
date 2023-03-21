import logging

from django.conf import settings
from vokativ import vokativ

from categories.models import PronounCategory
from ecomail import ecomail
from project.settings import EMAIL
from questionnaire.models import EventApplication

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

def application_created(application : EventApplication):
    email = (
        application.email or
        hasattr(application, "close_person") and application.close_person.email
    )
    if not email:
        logging.error("Application has no email to send notification to")
        return

    ecomail.send_email(
        EMAIL, SENDER_NAME,
        "Potvrzení přihlášení na akci", "147",
        [email],
        variables={
            **PronounCategory.get_variables(application.user),
            'vokativ': (
                    vokativ(application.nickname).capitalize() or
                    vokativ(application.first_name.split(' ')[0]).capitalize() or
                    application.user.vokativ
            ),
            'event_name': application.event_registration.event.name,
            'event_date': application.event_registration.event.get_date()
        }
    )

def event_created(event):
    return


def event_closed(event, auto=False):
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
