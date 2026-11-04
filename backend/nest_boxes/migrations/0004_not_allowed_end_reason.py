from django.db import migrations


def add_not_allowed(apps, schema_editor):
    NestBoxEndReason = apps.get_model("categories", "NestBoxEndReason")
    NestBoxEndReason.objects.update_or_create(
        slug="not_allowed",
        defaults=dict(name="nepovoleno", spot_reusable=False, order=3),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0020_nest_box_categories"),
        ("nest_boxes", "0003_simplify_boxes"),
    ]

    operations = [
        migrations.RunPython(add_not_allowed, migrations.RunPython.noop),
    ]
