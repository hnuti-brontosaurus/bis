from itertools import islice
from typing import Iterable, Iterator

from django.conf import settings
from django.core.management.base import BaseCommand

from bis.helpers import skip_ecomail_push
from bis.models import User, UserEmail
from categories.models import PronounCategory
from ecomail.sync import bulk_subscribe, get_session, iter_subscribers, remove_from_list

GENDER_TO_PRONOUN_SLUG = {
    "female": "woman",
    "male": "man",
}

ECOMAIL_TO_BIS_STATUS = {
    1: User.SubscriptionStatus.SUBSCRIBED,
    2: User.SubscriptionStatus.UNSUBSCRIBED,
    4: User.SubscriptionStatus.HARD_BOUNCE,
}

PULL_BATCH_SIZE = 100
PUSH_BATCH_SIZE = 100


def batched(iterable: Iterable, size: int) -> Iterator[list]:
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            return
        yield chunk


def clean_name(value):
    if not value:
        return ""
    value = " ".join(value.split())
    if "?" in value:
        return ""
    return value


def strip_plus_tag(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local.split('+', 1)[0]}@{domain}"


class Command(BaseCommand):
    help = (
        "Two-way sync between BIS and Ecomail. "
        "Pulls subscription status (and creates BIS users for new subscribed "
        "ecomail emails); pushes name, tags and per-user status back to ecomail; "
        "unsubscribes secondary BIS emails from ecomail."
    )

    def handle(self, *args, **options):
        list_id = settings.ECOMAIL_LIST_ID
        session = get_session()

        BASE_URL = "https://api2.ecomailapp.cz"

        response = session.put(
            f"{BASE_URL}/lists/{list_id}/update-subscriber",
            json={
                "email": "lamanchy@gmail.com",
                "subscriber_data": {
                    "tags": ["Test1"],
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        response = session.put(
            f"{BASE_URL}/lists/{list_id}/update-subscriber",
            json={
                "email": "alena.salajkova@gmail.com",
                "subscriber_data": {
                    "tags": ["Test1"],
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        response = session.post(
            f"{BASE_URL}/lists/{list_id}/subscribe-bulk",
            json={
                "subscriber_data": [
                    {
                        "email": "lamanchy@gmail.com",
                        "tags": ["Test5"],
                    },
                    {
                        "email": "alena.salajkova@gmail.com",
                        "tags": ["Test5"],
                    },
                ],
                "update_existing": True,
                "trigger_autoresponders": False,
            },
            timeout=120,
        )
        response.raise_for_status()

        return
        secondary_emails = []
        with skip_ecomail_push():
            secondary_emails = self._pull(session, list_id)

        # for email in secondary_emails:
        #     remove_from_list(session, list_id, email)

        self._push(session, list_id)

    def _pull(self, session, list_id):
        total = 0
        primary = 0
        created = 0
        pronoun_id_by_gender = {
            gender: PronounCategory.objects.get(slug=slug).id
            for gender, slug in GENDER_TO_PRONOUN_SLUG.items()
        }
        secondary_emails = []

        for batch in batched(iter_subscribers(session, list_id), PULL_BATCH_SIZE):
            parsed = [self._parse(item, pronoun_id_by_gender) for item in batch]
            total += len(parsed)

            for p in parsed:
                if p["email"] != p["raw_email"]:
                    secondary_emails.append(p["raw_email"])

            parsed = list({p["email"]: p for p in parsed}.values())

            emails = [p["email"] for p in parsed]
            email_to_user_id = {
                email: (user_id, user_email)
                for email, user_id, user_email in UserEmail.objects.filter(
                    email__in=emails
                ).values_list("email", "user_id", "user__email")
            }

            users_to_update = []
            for p in parsed:
                info = email_to_user_id.get(p["email"])
                if info is None:
                    if p["status"] == User.SubscriptionStatus.SUBSCRIBED:
                        User.objects.create(
                            email=p["email"],
                            first_name=p["name"],
                            last_name=p["surname"],
                            pronoun_id=p["pronoun_id"],
                            subscription_status=p["status"],
                        )
                        created += 1
                    continue

                user_id, user_email = info
                if p["email"] != user_email:
                    secondary_emails.append(p["email"])
                    continue

                if p["status"] is None:
                    continue

                users_to_update.append(
                    User(id=user_id, subscription_status=p["status"])
                )
                primary += 1

            if users_to_update:
                User.objects.bulk_update(users_to_update, ["subscription_status"])

            self.stdout.write(
                f"Pull: total={total}, primary={primary}, created={created}, "
                f"secondaries={len(secondary_emails)}"
            )

        return secondary_emails

    def _push(self, session, list_id):
        users = (
            # User.objects.filter(email__isnull=False)
            User.objects.filter(email="lamanchy@gmail.com")
            .select_related("pronoun", "address", "donor")
            .prefetch_related("roles")
            .iterator(chunk_size=PUSH_BATCH_SIZE)
        )
        pushed = 0
        for batch in batched(users, PUSH_BATCH_SIZE):
            bulk_subscribe(session, list_id, batch)
            pushed += len(batch)
            self.stdout.write(f"Push: {pushed}")

    def _parse(self, item: dict, pronoun_id_by_gender: dict) -> dict:
        subscriber = item["subscriber"]
        raw_email = item["email"].lower()
        return {
            "raw_email": raw_email,
            "email": strip_plus_tag(raw_email),
            "name": clean_name(subscriber.get("name")),
            "surname": clean_name(subscriber.get("surname")),
            "pronoun_id": pronoun_id_by_gender.get(subscriber.get("gender")),
            "status": ECOMAIL_TO_BIS_STATUS.get(item["status"]),
            "tags": subscriber.get("tags") or [],
        }
