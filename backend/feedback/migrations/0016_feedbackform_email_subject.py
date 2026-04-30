from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0015_remove_eventfeedback_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedbackform",
            name="email_subject",
            field=models.TextField(blank=True),
        ),
    ]
