from datetime import datetime, timezone

from django.db import migrations

LEGACY_UPLOAD_TIMESTAMP = datetime(2020, 1, 1, tzinfo=timezone.utc)


def backfill_legacy_timestamps(apps, schema_editor):
    EventPhoto = apps.get_model("event", "EventPhoto")
    EventAttendanceListPage = apps.get_model("event", "EventAttendanceListPage")
    EventPhoto.objects.filter(created_at__isnull=True).update(
        created_at=LEGACY_UPLOAD_TIMESTAMP
    )
    EventAttendanceListPage.objects.filter(created_at__isnull=True).update(
        created_at=LEGACY_UPLOAD_TIMESTAMP
    )


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0016_eventattendancelistpage_created_at_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_legacy_timestamps, migrations.RunPython.noop),
    ]
