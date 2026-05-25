from bis.email_validation import repair_email
from bis.helpers import paused_validation
from bis.models import User, UserEmail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Scan UserEmail rows and repair via repair_email(); rows that can't be "
        "repaired (or would collide with an existing email) are deleted. "
        "User.email is re-synced from the remaining UserEmail rows."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing to the database.",
        )

    def handle(self, *args, dry_run, **options):
        affected_user_ids = set()
        repaired = 0
        deleted = 0
        prefix = "[dry-run] " if dry_run else ""

        with paused_validation():
            for ue in UserEmail.objects.all():
                new = repair_email(ue.email)
                if new == ue.email:
                    continue
                affected_user_ids.add(ue.user_id)
                if (
                    new is None
                    or UserEmail.objects.filter(email=new).exclude(id=ue.id).exists()
                ):
                    self.stdout.write(
                        f"{prefix}delete UserEmail id={ue.id} user={ue.user_id} email={ue.email!r}"
                    )
                    if not dry_run:
                        ue.delete()
                    deleted += 1
                else:
                    self.stdout.write(
                        f"{prefix}repair UserEmail id={ue.id} user={ue.user_id} "
                        f"{ue.email!r} -> {new!r}"
                    )
                    if not dry_run:
                        ue.email = new
                        ue.save()
                    repaired += 1

            if not dry_run:
                for user in User.objects.filter(id__in=affected_user_ids):
                    first = getattr(user.all_emails.first(), "email", None)
                    if user.email != first:
                        user.email = first
                        user.save()

        self.stdout.write(
            f"{prefix}repair_emails: repaired {repaired}, deleted {deleted}, "
            f"affected {len(affected_user_ids)} users"
        )
