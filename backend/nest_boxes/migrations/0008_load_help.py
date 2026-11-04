from django.db import migrations
from nest_boxes.help_content import load_help


def load(apps, schema_editor):
    load_help(
        apps.get_model("nest_boxes", "HelpArticle"),
        apps.get_model("nest_boxes", "HelpImage"),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("nest_boxes", "0007_help_sources"),
    ]

    operations = [
        migrations.RunPython(load, migrations.RunPython.noop),
    ]
