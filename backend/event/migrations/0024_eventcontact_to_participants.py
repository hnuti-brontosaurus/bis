from bis.models import User
from django.db import migrations


def migrate_contacts_to_participants(apps, schema_editor):
    """Convert each EventContact into a participant on the corresponding record.

    Stale contacts on non-simple-list records are dropped; contacts without
    an email cannot be deduped and are also dropped. Uses the real User
    model so post_save signals fire — notably set_primary_email creates
    the matching UserEmail row that User.get(email=...) needs for future
    dedup.
    """
    EventContact = apps.get_model("event", "EventContact")

    for contact in EventContact.objects.select_related("record").iterator():
        if contact.record.attendance_list_type != "simple-list" or not contact.email:
            contact.delete()
            continue

        email = contact.email.lower().strip()
        user = User.get(email=email)
        if user is None:
            user = User(
                first_name=contact.first_name.strip() or "—",
                last_name=contact.last_name.strip() or "—",
                email=email,
                phone=contact.phone or "",
            )
            user.set_unusable_password()
            user.save()

        contact.record.participants.add(user.pk)
        contact.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0023_backfill_attendance_list_type"),
    ]

    operations = [
        migrations.RunPython(
            migrate_contacts_to_participants, migrations.RunPython.noop
        ),
    ]
