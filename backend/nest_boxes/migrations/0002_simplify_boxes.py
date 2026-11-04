from django.db import migrations, models

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
        migrations.RemoveField(
            model_name="nestbox",
            name="access_note",
        ),
        migrations.RemoveField(
            model_name="nestbox",
            name="batch",
        ),
        migrations.RemoveField(
            model_name="nestbox",
            name="elevation_source",
        ),
        migrations.RemoveField(
            model_name="nestbox",
            name="is_confirmed",
        ),
        migrations.RemoveField(
            model_name="nestbox",
            name="is_verified",
        ),
        migrations.RemoveField(
            model_name="nestbox",
            name="owner_note",
        ),
        migrations.RemoveField(
            model_name="nestbox",
            name="predator_guard",
        ),
        migrations.AlterField(
            model_name="nestbox",
            name="status",
            field=models.CharField(
                choices=[
                    ("planned", "plánovaná"),
                    ("in_use", "vyvěšená"),
                    ("taken_down", "sundaná na opravu"),
                    ("missing", "nenalezená"),
                    ("ended", "zaniklá"),
                ],
                max_length=15,
            ),
        ),
    ]
