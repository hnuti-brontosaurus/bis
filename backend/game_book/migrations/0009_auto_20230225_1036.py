from django.db import migrations


def migrate(apps, schema_editor):
    Tag = apps.get_model("game_book_categories", "Tag")
    Tag.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("game_book", "0008_alter_game_material"),
    ]

    operations = [migrations.RunPython(migrate, migrations.RunPython.noop)]
