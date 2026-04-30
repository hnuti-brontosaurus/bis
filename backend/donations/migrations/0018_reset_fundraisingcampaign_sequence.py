from django.db import migrations


def reset_sequence(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        "SELECT setval("
        "pg_get_serial_sequence('donations_fundraisingcampaign', 'id'), "
        "COALESCE((SELECT MAX(id) FROM donations_fundraisingcampaign), 1), "
        "(SELECT MAX(id) IS NOT NULL FROM donations_fundraisingcampaign)"
        ")"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("donations", "0017_rename_internal_note_donor_fundraisers_note_and_more"),
    ]

    operations = [
        migrations.RunPython(reset_sequence, migrations.RunPython.noop),
    ]
