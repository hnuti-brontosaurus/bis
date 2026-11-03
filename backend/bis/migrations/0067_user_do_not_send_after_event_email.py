from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0066_move_contact_preferences_to_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="do_not_send_after_event_email",
            field=models.BooleanField(default=False),
        ),
    ]
