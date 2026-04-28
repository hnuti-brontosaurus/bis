from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0056_subscription_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="organizers_note",
            field=models.TextField(
                blank=True,
                help_text=(
                    "Možnost přidat interní poznámku. Poznámku uvidí pouze lidé, "
                    "kteří si mohou tuto akci zobrazit přímo v BISu."
                ),
            ),
        ),
    ]
