from django.db import migrations


def could_not_open_to_reason(apps, schema_editor):
    NestBoxNotCleanedReason = apps.get_model("categories", "NestBoxNotCleanedReason")
    Check = apps.get_model("nest_boxes", "Check")
    reason, _ = NestBoxNotCleanedReason.objects.update_or_create(
        slug="could_not_open",
        defaults=dict(name="nešla otevřít", contents_known=False, order=2),
    )
    Check.objects.filter(cleaning="could_not_open").update(
        cleaning="not_cleaned", not_cleaned_reason=reason
    )


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0021_nest_box_not_cleaned_reason_contents"),
        ("nest_boxes", "0004_not_allowed_end_reason"),
    ]

    operations = [
        migrations.RunPython(could_not_open_to_reason, migrations.RunPython.noop),
    ]
