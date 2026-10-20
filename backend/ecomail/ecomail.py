import logging
import re

import sentry_sdk
from bis.helpers import are_emails_paused
from django.conf import settings
from ecomail.helpers import get_name_from_template, send
from ecomail.models import Contact
from ecomail.serializers import SendEmailSerializer
from lxml import html as lxml_html
from premailer import Premailer

_EMAIL_CSS = """
ul, ol, li {
    font-size: 16px;
    font-family: Ubuntu, Helvetica, Arial, sans-serif;
    color: #000000;
    line-height: 1.5;
}
p {
    font-size: 16px;
    margin: 0 0 13px;
}
a {
    color: #1E9646;
}
"""


def style_html(html: str) -> str:
    if not html:
        return html
    inlined = Premailer(
        html, css_text=_EMAIL_CSS, remove_classes=True, disable_validation=True
    ).transform()
    body = lxml_html.fromstring(inlined).find("body")
    if body is None:
        return inlined
    return (body.text or "") + "".join(
        lxml_html.tostring(child, encoding="unicode") for child in body
    )


UNRESOLVED_VARIABLE = re.compile(r"\*\|\w+\|\*")
REFUSED_RECIPIENT = re.compile(r"message\.to\.(\d+)\.email")


def report_refused(contact, template_id):
    # one Sentry issue per address, so only a newly refused one alerts
    with sentry_sdk.new_scope() as scope:
        scope.fingerprint = ["ecomail-refused-recipient", str(contact.id)]
        logging.error(
            "Ecomail refused recipient",
            extra={"data": {"template_id": template_id, "contact_id": contact.id}},
        )


def get_refused_contacts(response, contacts):
    # Ecomail answers every invalid field, and a blocked account too, with a 422;
    # only an invalid recipient is the address's fault rather than ours
    matches = [REFUSED_RECIPIENT.fullmatch(key) for key in response.get("errors", {})]
    if not matches or not all(matches):
        return []
    return [contacts[int(match[1])] for match in matches]


def replace_variables(html: str, variables: dict[str, str]) -> str:
    for name, value in variables.items():
        html = html.replace(f"*|{name}|*", str(value))
    return html


def send_email(
    sender: tuple[str, str],
    template_id: int,
    recipients: list[str],
    *,
    subject=None,
    reply_to=None,
    variables=None,
    attachments=None,
):
    from_name, from_email = sender
    if attachments is None:
        attachments = []
    if variables is None:
        variables = {}
    if reply_to is None:
        reply_to = [from_email]
    if subject is None:
        subject = replace_variables(get_name_from_template(template_id), variables)
    recipients = [recipient for recipient in recipients if recipient]

    if UNRESOLVED_VARIABLE.search(subject):
        logging.error(
            "Email subject has unknown variables",
            extra={"data": {"template_id": template_id, "subject": subject}},
        )

    data = dict(
        from_email=from_email,
        from_name=from_name,
        subject=subject,
        template_id=template_id,
        recipients=recipients,
        variables=variables,
        attachments=attachments,
        reply_to=reply_to,
    )

    if settings.ENVIRONMENT != "prod" or are_emails_paused():
        # local password resets are read from here; anywhere else the
        # variables are real people's data
        logging.info(
            "Skipping email, sending disabled",
            extra={"data": data if settings.DEBUG else {"template_id": template_id}},
        )
        return

    if not recipients:
        logging.warning(
            "Skipping email, no recipients",
            extra={"data": {"template_id": template_id}},
        )
        return

    SendEmailSerializer(data=data).is_valid(raise_exception=True)

    message = {
        "template_id": template_id,
        "subject": subject,
        "from_name": from_name,
        "from_email": from_email,
        "reply_to": ",".join(reply_to),
        "global_merge_vars": [
            {"name": key, "content": value} for key, value in variables.items()
        ],
        "attachments": [
            {
                "type": attachment["content_type"],
                "name": attachment["name"],
                "content": attachment["data"],
            }
            for attachment in attachments
        ],
    }

    def send_to(contacts):
        to = [{"email": contact.email} for contact in contacts]
        return send(
            contacts,
            "POST",
            "transactional/send-template",
            {"message": message | {"to": to}},
        )

    contacts = [Contact.objects.get_or_create(email=email)[0] for email in recipients]
    res = send_to(contacts)

    # Ecomail lists every invalid address at once, so one resend is enough
    if refused := get_refused_contacts(res, contacts):
        for contact in refused:
            report_refused(contact, template_id)
        contacts = [contact for contact in contacts if contact not in refused]
        if not contacts:
            return
        res = send_to(contacts)

    if "results" not in res:
        raise RuntimeError(f"Ecomail API error: {res}")

    assert res["results"]["total_accepted_recipients"] == len(contacts)
    logging.info(
        "Sent email",
        extra={
            "data": {
                "template_id": template_id,
                "contact_ids": [contact.id for contact in contacts],
            }
        },
    )
