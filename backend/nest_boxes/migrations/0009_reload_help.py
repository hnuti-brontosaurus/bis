from django.db import migrations
from nest_boxes.help_content import load_help


def reload(apps, schema_editor):
    """Back to the shipped help, now that only budkaři manage areas."""
    HelpArticle = apps.get_model("nest_boxes", "HelpArticle")
    HelpImage = apps.get_model("nest_boxes", "HelpImage")
    for image in HelpImage.objects.all():
        # django_cleanup does not watch a migration's models
        image.image.delete(save=False)
        image.delete()
    HelpArticle.objects.update(content="")
    load_help(HelpArticle, HelpImage)


class Migration(migrations.Migration):
    dependencies = [
        ("nest_boxes", "0008_load_help"),
    ]

    operations = [
        migrations.RunPython(reload, migrations.RunPython.noop),
    ]
