from django.db import migrations


def merge_call_declined(apps, schema_editor):
    DonorEvent = apps.get_model("donations", "DonorEvent")
    DonorEventCategory = apps.get_model("categories", "DonorEventCategory")

    try:
        no_answer = DonorEventCategory.objects.get(slug="call_no_answer")
    except DonorEventCategory.DoesNotExist:
        return

    DonorEvent.objects.filter(event_type__slug="call_declined").update(
        event_type=no_answer
    )
    DonorEventCategory.objects.filter(slug="call_declined").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("donations", "0018_reset_fundraisingcampaign_sequence"),
        ("categories", "0017_donoreventcategory"),
    ]

    operations = [
        migrations.RunPython(merge_call_declined, migrations.RunPython.noop),
    ]
