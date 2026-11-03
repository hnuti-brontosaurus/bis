from django.db import migrations

PREFERENCES = ("do_not_call", "do_not_solicit")


def copy_to_user(apps, schema_editor):
    User = apps.get_model("bis", "User")
    for preference in PREFERENCES:
        User.objects.filter(**{f"donor__{preference}": True}).update(
            **{preference: True}
        )


def copy_to_donor(apps, schema_editor):
    Donor = apps.get_model("donations", "Donor")
    for preference in PREFERENCES:
        Donor.objects.filter(**{f"user__{preference}": True}).update(
            **{preference: True}
        )


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0066_move_contact_preferences_to_user"),
        ("donations", "0020_donation_donations_d_donated_7b0c04_idx_and_more"),
    ]

    operations = [
        migrations.RunPython(copy_to_user, copy_to_donor),
        migrations.RemoveField(model_name="donor", name="do_not_call"),
        migrations.RemoveField(model_name="donor", name="do_not_solicit"),
    ]
