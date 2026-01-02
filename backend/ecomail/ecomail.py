import logging

from django.conf import settings
from django.core.cache import cache
from ecomail.helpers import send
from ecomail.models import Contact
from ecomail.serializers import SendEmailSerializer

# def delete_contact(email):
#     if settings.TEST: return
#     DeleteContactSerializer(data=dict(email=email)).is_valid(raise_exception=True)
#
#     contact, _ = Contact.objects.get_or_create(email=email)
#     response = send(contact, "GET", f"REST/contact/{email}")
#
#     # if contact exists in ecomail
#     if 'Data' in response:
#         id = response["Data"][0]["ID"]
#         send(contact, "DELETE", f"contacts/{id}", version="v4")
#
#
# def create_contact(email, data: dict = None):
#     if settings.TEST: return
#     if data is None:
#         data = {}
#     CreateContactSerializer(data=dict(email=email, data=data)).is_valid(raise_exception=True)
#
#     contact, _ = Contact.objects.get_or_create(email=email)
#
#     send(contact, "POST", "REST/contact", {
#         "Email": email
#     })
#     send(contact, "PUT", f"REST/contactdata/{email}", {
#         "Data": [
#             {
#                 "Name": key,
#                 "Value": value
#             } for key, value in data.items()
#         ]
#     })
#
#
# def set_subscription_status(email, list_id, is_subscribed):
#     if settings.TEST: return
#     SetSubscriptionStatusSerializer(data=dict(email=email, list_id=list_id, is_subscribed=is_subscribed)).is_valid(
#         raise_exception=True)
#
#     contact, _ = Contact.objects.get_or_create(email=email)
#     send(contact, "POST", f"REST/listrecipient", {
#         "ContactAlt": email,
#         "ListID": list_id,
#         "IsUnsubscribed": "true"
#     })
#
#     res = send(contact, "GET", f"REST/listrecipient", params={
#         "ContactEmail": email,
#         "ContactsList": list_id
#     })
#     id = res["Data"][0]["ID"]
#
#     send(contact, "PUT", f"REST/listrecipient/{id}", {
#         "IsUnsubscribed": str(not is_subscribed).lower()
#     })


def send_email(
    sender: tuple[str, str],
    subject: str,
    template_id: int,
    recipients: list[str],
    *,
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
        print("Sending of emails disabled, email data:", data)
        return

    if not recipients:
        logging.exception("No recipients for email", extra=data)
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
    assert res["results"]["total_accepted_recipients"] == len(recipients)
    print("SENT EMAIL", f"{subject=},\t{from_email=},\t{from_name=},\t{recipients=}")
