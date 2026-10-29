import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("donations", "0023_move_campaign_events_to_user")]

    operations = [
        migrations.RemoveField(model_name="donorevent", name="donor"),
        migrations.AlterField(
            model_name="donorevent",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="campaign_events",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
