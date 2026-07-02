import uuid

from django.db import migrations, models


def populate_uid(apps, schema_editor):
    Event = apps.get_model("bis", "Event")
    for event in Event.objects.all().only("id"):
        Event.objects.filter(pk=event.pk).update(uid=uuid.uuid4())


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0060_alter_event__search_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="shared_folder_url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="event",
            name="uid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.RunPython(populate_uid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="event",
            name="uid",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, null=True, unique=True
            ),
        ),
    ]
