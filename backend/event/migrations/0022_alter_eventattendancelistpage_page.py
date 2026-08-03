from django.db import migrations, models


def blank_out_null_pages(apps, schema_editor):
    EventAttendanceListPage = apps.get_model("event", "EventAttendanceListPage")
    EventAttendanceListPage.objects.filter(page__isnull=True).update(page="")


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0021_move_section_event_to_section_meeting"),
    ]

    operations = [
        migrations.RunPython(blank_out_null_pages, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="eventattendancelistpage",
            name="page",
            field=models.FileField(blank=True, upload_to="attendance_list_pages"),
        ),
    ]
