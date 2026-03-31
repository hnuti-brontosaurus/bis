import logging

from django.conf import settings
from django.core.cache import cache

from ecomail.helpers import get_name_from_template, send
from ecomail.models import Contact
from ecomail.serializers import SendEmailSerializer


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
    if subject is None:
        subject = get_name_from_template(template_id)
    if attachments is None:
        attachments = []
    if variables is None:
        variables = {}
    if reply_to is None:
        reply_to = [from_email]
    recipients = [recipient for recipient in recipients if recipient]

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

    if settings.TEST or not settings.EMAILS_ENABLED or cache.get("emails_paused"):
        logging.info("Sending of emails disabled, email data: %s", data)
        return

    if not recipients:
        logging.warning("No recipients for email", extra=data)
        return

    SendEmailSerializer(data=data).is_valid(raise_exception=True)

    contacts = [Contact.objects.get_or_create(email=email)[0] for email in recipients]
    res = send(
        contacts,
        "POST",
        f"transactional/send-template",
        {
            "message": {
                "template_id": template_id,
                "subject": subject,
                "from_name": from_name,
                "from_email": from_email,
                "reply_to": ",".join(reply_to),
                "to": [{"email": contact.email} for contact in contacts],
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
        },
    )

    if "results" not in res:
        raise RuntimeError(f"Ecomail API error: {res}")

    assert res["results"]["total_accepted_recipients"] == len(recipients)
    logging.info(
        "SENT EMAIL subject=%s, from_email=%s, from_name=%s, recipients=%s",
        subject,
        from_email,
        from_name,
        recipients,
    )
