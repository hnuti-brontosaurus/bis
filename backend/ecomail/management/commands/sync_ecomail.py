from datetime import UTC, datetime, timedelta

from bis.helpers import print_progress, skip_ecomail_push
from bis.models import User, UserEmail
from categories.models import PronounCategory
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from ecomail.sync import (
    PUSH_BATCH_SIZE,
    batched,
    get_session,
    iter_subscribers,
    push_users,
    remove_from_list,
)

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


def _parse_ecomail_datetime(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


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

    def add_arguments(self, parser):
        parser.add_argument(
            "--input-list-id",
            type=int,
            default=settings.ECOMAIL_LIST_ID,
            help="Ecomail list to pull subscribers from.",
        )
        parser.add_argument(
            "--output-list-id",
            type=int,
            default=settings.ECOMAIL_LIST_ID,
            help="Ecomail list to push BIS users to.",
        )
        parser.add_argument(
            "--promotion-window-days",
            type=int,
            default=7,
            help=(
                "Window (in days) within which a recently-added secondary email "
                "is promoted over a still-subscribed primary."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't write to BIS or Ecomail; just print what the sync would do.",
        )

    def handle(
        self,
        *args,
        input_list_id,
        output_list_id,
        promotion_window_days,
        dry_run,
        **options,
    ):
        session = get_session()

        with skip_ecomail_push():
            secondary_emails = self._pull(
                session, input_list_id, timedelta(days=promotion_window_days), dry_run
            )

        if dry_run:
            self.stdout.write(
                f"[dry-run] would unsubscribe {len(secondary_emails)} secondary emails"
            )
            self.stdout.write(
                f"[dry-run] would push {User.objects.filter(email__isnull=False).count()} users"
            )
            return

        if input_list_id == output_list_id:
            for i, email in enumerate(secondary_emails):
                remove_from_list(session, input_list_id, email)
                print_progress(
                    "ecomail sync: removing secondaries", i, len(secondary_emails)
                )

        self._push(session, output_list_id)

    def _pull(self, session, list_id, promotion_window, dry_run=False):
        total = 0
        primary = 0
        created = 0
        promoted = 0
        pronoun_id_by_gender = {
            gender: PronounCategory.objects.get(slug=slug).id
            for gender, slug in GENDER_TO_PRONOUN_SLUG.items()
        }
        secondary_emails = []
        promotion_cutoff = now() - promotion_window

        for batch in batched(iter_subscribers(session, list_id), PULL_BATCH_SIZE):
            parsed = [self._parse(item, pronoun_id_by_gender) for item in batch]
            total += len(parsed)

            secondary_emails.extend(
                p["raw_email"] for p in parsed if p["email"] != p["raw_email"]
            )

            parsed = list({p["email"]: p for p in parsed}.values())

            emails = [p["email"] for p in parsed]
            email_to_user = {
                email: (user_id, user_email, user_status)
                for email, user_id, user_email, user_status in UserEmail.objects.filter(
                    email__in=emails
                ).values_list(
                    "email", "user_id", "user__email", "user__subscription_status"
                )
            }

            users_to_update = []
            promoted_user_ids = set()
            for p in parsed:
                info = email_to_user.get(p["email"])
                if info is None:
                    if p["status"] == User.SubscriptionStatus.SUBSCRIBED:
                        if not dry_run:
                            User.objects.create(
                                email=p["email"],
                                first_name=p["name"],
                                last_name=p["surname"],
                                pronoun_id=p["pronoun_id"],
                                subscription_status=p["status"],
                            )
                        created += 1
                    continue

                user_id, user_email, user_status = info
                if p["email"] != user_email:
                    if self._should_promote(p, user_status, promotion_cutoff):
                        if not dry_run:
                            user = User.objects.get(id=user_id)
                            user.email = p["email"]
                            user.subscription_status = (
                                User.SubscriptionStatus.SUBSCRIBED
                            )
                            user.save()
                        promoted_user_ids.add(user_id)
                        promoted += 1
                    else:
                        secondary_emails.append(p["email"])
                    continue

                if p["status"] is None:
                    continue

                users_to_update.append(
                    User(id=user_id, subscription_status=p["status"])
                )
                primary += 1

            users_to_update = [
                u for u in users_to_update if u.id not in promoted_user_ids
            ]
            if users_to_update and not dry_run:
                User.objects.bulk_update(users_to_update, ["subscription_status"])

            prefix = "[dry-run] " if dry_run else ""
            self.stdout.write(
                f"{prefix}Pull: total={total}, primary={primary}, created={created}, "
                f"promoted={promoted}, secondaries={len(secondary_emails)}"
            )

        return secondary_emails

    @staticmethod
    def _should_promote(parsed, user_status, promotion_cutoff):
        if parsed["status"] != User.SubscriptionStatus.SUBSCRIBED:
            return False
        if user_status != User.SubscriptionStatus.SUBSCRIBED:
            return True
        inserted_at = parsed["inserted_at"]
        return inserted_at is not None and inserted_at >= promotion_cutoff

    def _push(self, session, list_id):
        base = User.objects.filter(email__isnull=False)
        total = base.count()
        pushed = 0
        id_iter = base.values_list("id", flat=True).iterator(chunk_size=PUSH_BATCH_SIZE)
        for batch_ids in batched(id_iter, PUSH_BATCH_SIZE):
            pushed += push_users(session, list_id, batch_ids)
            print_progress("ecomail sync: pushing users", pushed - 1, total)

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
            "inserted_at": _parse_ecomail_datetime(item.get("inserted_at")),
        }
