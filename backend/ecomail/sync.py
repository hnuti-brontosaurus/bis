import logging
from typing import Iterable, Iterator

from django.conf import settings
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from bis.models import User
from ecomail.tags import compute_tags

BASE_URL = "https://api2.ecomailapp.cz"

PRONOUN_SLUG_TO_GENDER = {
    "woman": "female",
    "man": "male",
}


def get_session() -> Session:
    session = Session()
    retries = Retry(
        total=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PUT", "DELETE"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"key": settings.ECOMAIL_API_KEY})
    return session


def iter_subscribers(
    session: Session, list_id: int, per_page: int = 100
) -> Iterator[dict]:
    page = 1
    while True:
        response = session.get(
            f"{BASE_URL}/lists/{list_id}/subscribers",
            params={"per_page": per_page, "page": page},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        for subscriber in data["data"]:
            yield subscriber
        if data["next_page_url"] is None:
            return
        page += 1


def _user_to_subscriber_data(user: User) -> dict:
    address = getattr(user, "address", None)
    donor = getattr(user, "donor", None)
    return {
        "status": user.subscription_status,
        "name": user.first_name,
        "surname": user.last_name,
        "tags": compute_tags(user),
        "vokativ": user.vokativ,
        "phone": str(user.phone) if user.phone else None,
        "birthday": user.birthday.isoformat() if user.birthday else None,
        "gender": PRONOUN_SLUG_TO_GENDER.get(user.pronoun and user.pronoun.slug),
        "street": address.street if address else None,
        "city": address.city if address else None,
        "zip": address.zip_code if address else None,
        "custom_fields": {
            "nickname": user.nickname,
            "pronoun": user.pronoun.name if user.pronoun else None,
            "full_name": user.get_name(),
            "short_name": user.get_name(show_nickname=False),
            "proper_name": user.get_proper_name(),
            "formal_vokativ": donor.formal_vokativ if donor else None,
        },
    }


def bulk_subscribe(
    session: Session,
    list_id: int,
    users: Iterable[User],
) -> None:
    payloads = [
        {"email": user.email, **_user_to_subscriber_data(user)} for user in users
    ]
    if not payloads:
        return

    if settings.ENVIRONMENT != "prod":
        logging.info("[dummy] bulk_subscribe list=%s payloads=%s", list_id, payloads)
        return

    response = session.post(
        f"{BASE_URL}/lists/{list_id}/subscribe-bulk",
        json={
            "subscriber_data": payloads,
            "update_existing": True,
            "trigger_autoresponders": False,
        },
        timeout=120,
    )
    response.raise_for_status()


def remove_from_list(session: Session, list_id: int, email: str) -> None:
    if settings.ENVIRONMENT != "prod":
        logging.info("[dummy] remove_from_list list=%s email=%s", list_id, email)
        return

    response = session.delete(
        f"{BASE_URL}/lists/{list_id}/unsubscribe",
        json={"email": email},
        timeout=30,
    )
    response.raise_for_status()
