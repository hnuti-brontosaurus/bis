from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nest_boxes", "0002_simplify_box_data"),
    ]

    operations = [
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
                    ("in_use", "v pořádku"),
                    ("needs_repair", "potřebuje opravu"),
                    ("needs_replacing", "potřebuje vyměnit"),
                    ("taken_down", "sundaná na opravu"),
                    ("missing", "nenalezená"),
                    ("ended", "zaniklá"),
                ],
                max_length=15,
            ),
        ),
    ]
