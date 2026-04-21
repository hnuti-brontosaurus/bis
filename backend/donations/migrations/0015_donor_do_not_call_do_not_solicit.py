from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("donations", "0014_donorevent_rename_prislib_to_pledge"),
    ]

    operations = [
        migrations.AddField(
            model_name="donor",
            name="do_not_call",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="donor",
            name="do_not_solicit",
            field=models.BooleanField(default=False),
        ),
    ]
