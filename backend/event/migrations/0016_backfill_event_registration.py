from django.db import migrations


def create_default_registrations(apps, schema_editor):
    Event = apps.get_model("event", "Event")
    EventRegistration = apps.get_model("event", "EventRegistration")

    missing = Event.objects.filter(registration__isnull=True)
    EventRegistration.objects.bulk_create(
        [EventRegistration(event=event) for event in missing]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0015_eventrecord_is_event_closed_email_enabled"),
    ]

    operations = [
        migrations.RunPython(create_default_registrations, migrations.RunPython.noop),
    ]
