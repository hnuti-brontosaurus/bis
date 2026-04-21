from django.db import migrations


def delete_category(apps, schema_editor):
    DonorEventCategory = apps.get_model("categories", "DonorEventCategory")
    DonorEventCategory.objects.filter(slug="removed_from_campaign").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("donations", "0010_donorevent_campaign_required"),
    ]

    operations = [
        migrations.RunPython(delete_category, migrations.RunPython.noop),
    ]
