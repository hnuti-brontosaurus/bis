"""
todo: teď to neupdatuje s více uživateli, jen po jednom
todo: z malyjan mi to neoddělá tag 'tmp', i když by mělo
todo: vypadá, že jsou to spíš problémy ecomailu než kódu

potom je potřeba přepsat settings na 28!!!!!!!!
a taky necommitovat import_old_opportunities!
"""
import logging
from pprint import pprint

from django.contrib import admin
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from bis.models import User
from project.settings import ECOMAIL_API_KEY, ECOMAIL_LIST_ID

logger = logging.getLogger(__name__)


def get_session() -> Session:
    session = Session()
    retries = Retry(
        total=4,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def compute_tags():
    # TODO
    raise NotImplementedError
    # something like this:
    for user in User.objects.all():
        if user.is_active and user.date_joined > now:
            mladi_aktivni.add(user)


def bulk_update_ecomail(session: Session, user_list: list[dict], list_id: int):
    """
    https://docs.ecomail.cz/api-reference/lists/subscribe-bulk
    Limited to 3000 subscribers per call — subscribers above the limit are ignored!!!
    """
    data = {
        "subscriber_data": user_list,
        "update_existing": True,
        "resubscribe": False,
        "trigger_autoresponders": False,
    }
    response = session.post(
        f"https://api2.ecomailapp.cz/lists/{list_id}/subscribe-bulk",
        json=data,
        headers={"key": ECOMAIL_API_KEY},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def get_email_to_tags_mapping(session: Session, list_id: int) -> dict[str, list[str]]:
    """
    execution time: ~ 9 s for 11k subscribers we have in ecomail
    (per_page=2000 seems most reasonable from testing)
    https://docs.ecomail.cz/api-reference/lists/get-subscribers
    """
    email_to_tags = {}
    next_page = True
    i = 0
    while next_page:
        response = session.get(
            f"https://api2.ecomailapp.cz/lists/{list_id}/subscribers",
            headers={"key": ECOMAIL_API_KEY},
            params={"per_page": 2000, "page": i},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        # pprint(data)
        for subscriber in data["data"]:
            email = subscriber.get("subscriber").get("email", None)
            if email:
                email_to_tags[email.lower()] = (
                    subscriber.get("subscriber", {}).get("tags") or []
                )
        if data["next_page_url"] is None:
            next_page = False
        i += 1

    return email_to_tags


@admin.action(description="Vytvoř dočasný štítek (tmp) v ecomailu")
def create_tmp_tag(model_admin, request, queryset):
    session = get_session()

    queryset_emails = set(
        queryset.exclude(email__isnull=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    queryset_emails = {email.lower() for email in queryset_emails}

    email_to_tags_mapping = get_email_to_tags_mapping(session, ECOMAIL_LIST_ID)

    user_list = []

    # existing subscribers from ecomail
    for email, tags in email_to_tags_mapping.items():
        has_tmp = "tmp" in tags

        if email in queryset_emails:
            if not has_tmp:
                tags.append("tmp")
                user_list.append({"email": email, "tags": tags})
            # if the subscriber already has the 'tmp' tag, do nothing and save requests
        else:
            if has_tmp:
                tags.remove("tmp")
                user_list.append({"email": email, "tags": tags})

    # add new subscribers from queryset to ecomail
    for email in queryset_emails:
        if email not in email_to_tags_mapping.keys():
            user_list.append({"email": email, "tags": ["tmp"]})

    # bulk update
    if not user_list:
        return model_admin.message_user(
            request, "Žádná změna nebyla potřeba.", level="info"
        )

    batch_size = 3000
    for i in range(0, len(user_list), batch_size):
        chunk = user_list[i : i + batch_size]
        try:
            bulk_update_ecomail(session, chunk, ECOMAIL_LIST_ID)
        except Exception as e:
            logger.error(
                f"Failed to update ecomail (chunk no. '{i}', ecomail_list_id '{ECOMAIL_LIST_ID}'): {e}"
            )

    return model_admin.message_user(
        request, "Hurá! Vybrané uživatele najdeš pod štítkem 'tmp' v ecomailu."
    )
