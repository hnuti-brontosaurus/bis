import common.thumbnails
from django.db import migrations


def blank_out_null_photos(apps, schema_editor):
    User = apps.get_model("bis", "User")
    User.objects.filter(photo__isnull=True).update(photo="")


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0061_event_shared_folder_url_event_uid"),
    ]

    operations = [
        migrations.RunPython(blank_out_null_photos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="photo",
            field=common.thumbnails.ThumbnailImageField(
                blank=True, upload_to="user_photos"
            ),
        ),
    ]
