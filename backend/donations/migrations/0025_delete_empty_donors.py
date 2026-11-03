import datetime

from django.db import migrations

# GIFTLESS_DONOR_CUTOFF in ecomail/tags.py: profiles from before it are legacy
# donors whose gifts predate the donation records.
LEGACY_CUTOFF = datetime.date(2023, 1, 1)


def delete_empty_donors(apps, schema_editor):
    """Profiles that adding a user to a campaign used to create. Campaigns are
    kept on the user now, so a profile with nothing in it is no donor."""
    Donor = apps.get_model("donations", "Donor")
    Donor.objects.filter(
        date_joined__gte=LEGACY_CUTOFF,
        donations__isnull=True,
        pledges__isnull=True,
        variable_symbols__isnull=True,
        company__isnull=True,
        fundraisers_note="",
        formal_vokativ="",
        regional_center_support__isnull=True,
        basic_section_support__isnull=True,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("donations", "0024_remove_donor_from_campaign_events")]

    operations = [migrations.RunPython(delete_empty_donors, migrations.RunPython.noop)]
