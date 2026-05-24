from django.db import migrations
from django.db.models import Count, Exists, OuterRef


def backfill(apps, schema_editor):
    EventRecord = apps.get_model("event", "EventRecord")
    EventContact = apps.get_model("event", "EventContact")

    rows = EventRecord.objects.annotate(
        participant_count=Count("participants"),
        has_contacts=Exists(EventContact.objects.filter(record=OuterRef("pk"))),
    ).values_list(
        "pk",
        "participant_count",
        "has_contacts",
        "number_of_participants",
        "event__group__slug",
    )

    full_list, simple_list, count = [], [], []
    for pk, participant_count, has_contacts, number_of_participants, group_slug in rows:
        if group_slug != "other" or participant_count:
            full_list.append(pk)
        elif has_contacts:
            simple_list.append(pk)
        elif number_of_participants is not None:
            count.append(pk)

    EventRecord.objects.filter(pk__in=full_list).update(
        attendance_list_type="full-list"
    )
    EventRecord.objects.filter(pk__in=simple_list).update(
        attendance_list_type="simple-list"
    )
    EventRecord.objects.filter(pk__in=count).update(attendance_list_type="count")


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0022_eventrecord_attendance_list_type"),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
