from django.db import migrations


def backfill(apps, schema_editor):
    EventRecord = apps.get_model("event", "EventRecord")

    EventRecord.objects.filter(attendance_list_type__isnull=True).exclude(
        event__group__slug="other"
    ).update(attendance_list_type="full-list")


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0026_delete_eventcontact"),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
