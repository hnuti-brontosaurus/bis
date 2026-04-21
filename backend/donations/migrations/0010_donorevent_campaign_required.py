import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0018_fundraisingcampaigncategory"),
        ("donations", "0009_backfill_automatic_emails_campaign"),
    ]

    operations = [
        migrations.AlterField(
            model_name="donorevent",
            name="campaign",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="events",
                to="categories.fundraisingcampaigncategory",
            ),
        ),
    ]
