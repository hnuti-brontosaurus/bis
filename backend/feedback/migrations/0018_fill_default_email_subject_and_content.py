from django.db import migrations

DEFAULT_EMAIL_SUBJECT = "Jaký to bylo? Zpětná vazba z akce"

DEFAULT_EMAIL_CONTENT = """
        <p>Ahoj *|vokativ|*,</p>
        <p>&hellip; doufáme, že se po *|event_name|* cítíš jenom dobře! 😊</p>
        <p><br></p>
        <p> A teď upřímně — <b>jaký to bylo?</b></p>
        <p>Když připravujeme akce, vždycky se opíráme hlavně o to, co nám napíšete do zpětné vazby.</p>
        <p><i>Podle ní ladíme program, atmosféru i to, co má na akcích opravdu smysl.</i></p>
        <p><br></p>
        <p>Takže&hellip; jestli nám můžeš věnovat pár minut, moc nám to pomůže. 🙏💚</p>
      """


def fill_defaults(apps, schema_editor):
    FeedbackForm = apps.get_model("feedback", "FeedbackForm")
    FeedbackForm.objects.filter(email_subject="").update(
        email_subject=DEFAULT_EMAIL_SUBJECT
    )
    FeedbackForm.objects.filter(email_content="").update(
        email_content=DEFAULT_EMAIL_CONTENT
    )


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0017_alter_feedbackform_email_content_and_more"),
    ]

    operations = [
        migrations.RunPython(fill_defaults, migrations.RunPython.noop),
    ]
