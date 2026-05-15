from django.db import migrations


def move_section_event_to_section_meeting(apps, schema_editor):
    EventCategory = apps.get_model("categories", "EventCategory")
    Event = apps.get_model("bis", "Event")

    section_event = EventCategory.objects.filter(slug="section_event").first()
    if section_event is None:
        return

    section_meeting = EventCategory.objects.get(slug="section_meeting")
    Event.objects.filter(category=section_event).update(category=section_meeting)
    section_event.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0020_merge_20260428_1246"),
        ("categories", "0019_remove_fundraisingcampaigncategory"),
    ]

    operations = [
        migrations.RunPython(
            move_section_event_to_section_meeting, migrations.RunPython.noop
        ),
    ]
