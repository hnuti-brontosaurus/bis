from django.db import migrations
from django.db.models import OuterRef, Subquery


def copy_to_user(apps, schema_editor):
    DonorEvent = apps.get_model("donations", "DonorEvent")
    Donor = apps.get_model("donations", "Donor")
    DonorEvent.objects.update(
        user=Subquery(Donor.objects.filter(pk=OuterRef("donor")).values("user"))
    )


def copy_to_donor(apps, schema_editor):
    DonorEvent = apps.get_model("donations", "DonorEvent")
    Donor = apps.get_model("donations", "Donor")
    users = DonorEvent.objects.values_list("user", flat=True).distinct()
    for user in users.exclude(user__donor__isnull=False):
        Donor.objects.create(user_id=user)
    DonorEvent.objects.update(
        donor=Subquery(Donor.objects.filter(user=OuterRef("user")).values("pk"))
    )


# Its own migration: going back creates donor profiles, and postgres refuses to
# alter a table that rows inserted earlier in the same transaction refer to.
class Migration(migrations.Migration):
    dependencies = [("donations", "0022_add_user_to_campaign_events")]

    operations = [migrations.RunPython(copy_to_user, copy_to_donor)]
