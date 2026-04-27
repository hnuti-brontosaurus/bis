from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0017_backfill_upload_timestamps"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventattendancelistpage",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="eventphoto",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
