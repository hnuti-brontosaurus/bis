import common.thumbnails
from django.db import migrations


def blank_out_null_photos(apps, schema_editor):
    RecipeStep = apps.get_model("cookbook", "RecipeStep")
    RecipeStep.objects.filter(photo__isnull=True).update(photo="")


class Migration(migrations.Migration):
    dependencies = [
        ("cookbook", "0025_alter_ingredient_state"),
    ]

    operations = [
        migrations.RunPython(blank_out_null_photos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="recipestep",
            name="photo",
            field=common.thumbnails.ThumbnailImageField(
                blank=True, upload_to="recipe_steps"
            ),
        ),
    ]
