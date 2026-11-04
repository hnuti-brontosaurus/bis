from django.db import migrations

RETIRED_END_REASONS = ("replaced", "unsuitable", "not_allowed")


def simplify(apps, schema_editor):
    NestBox = apps.get_model("nest_boxes", "NestBox")
    NestBoxEndReason = apps.get_model("categories", "NestBoxEndReason")

    # A plan that was never hung is deleted now, not cancelled
    NestBox.objects.filter(status="cancelled").delete()
    # A volunteer's new box is a planned box now, hung by its check
    NestBox.objects.filter(is_confirmed=False).update(status="planned")

    retired = NestBoxEndReason.objects.filter(slug__in=RETIRED_END_REASONS)
    if retired.exists():
        NestBox.objects.filter(end_reason__in=retired).update(
            end_reason=NestBoxEndReason.objects.get(slug="worn_out")
        )
        retired.delete()

    for box in NestBox.objects.exclude(access_note=""):
        box.note = "\n".join(filter(None, [box.access_note, box.note]))
        box.save(update_fields=["note"])


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0020_nest_box_categories"),
        ("nest_boxes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(simplify, migrations.RunPython.noop),
    ]
