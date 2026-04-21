from django.db import migrations


def backfill(apps, schema_editor):
    FundraisingCampaignCategory = apps.get_model(
        "categories", "FundraisingCampaignCategory"
    )
    DonorEvent = apps.get_model("donations", "DonorEvent")

    campaign, _ = FundraisingCampaignCategory.objects.get_or_create(
        slug="automatic_emails",
        defaults={"name": "Automatické e-maily"},
    )
    DonorEvent.objects.filter(campaign__isnull=True).update(campaign=campaign)


class Migration(migrations.Migration):
    dependencies = [
        ("donations", "0008_donorevent_fundraising_fields"),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
