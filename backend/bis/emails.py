from django.conf import settings

from ecomail import ecomail
from project.settings import EMAIL

SENDER_NAME = 'BIS'


def password_reset_link(user, email, login_code):
    text(email, 'Link pro (pře)nastavení hesla, platný jednu hodinu',
         f'{settings.FULL_HOSTNAME}/reset_password'
         f'?email={email}'
         f'&code={login_code.code}'
         f'&password_exists={user.has_usable_password()}')


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
