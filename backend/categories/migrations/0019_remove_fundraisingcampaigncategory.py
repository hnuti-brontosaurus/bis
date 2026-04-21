from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0018_fundraisingcampaigncategory"),
        ("donations", "0012_move_fundraising_campaign"),
    ]

    operations = [
        migrations.DeleteModel(
            name="FundraisingCampaignCategory",
        ),
    ]
