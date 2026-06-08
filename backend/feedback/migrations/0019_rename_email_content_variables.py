from django.db import migrations

RENAMES = {
    "*|vokativ|*": "*|osloveni|*",
    "*|event_name|*": "*|nazev_akce|*",
}

OLD_DEFAULT_SUBJECT = "Jaký to bylo? Zpětná vazba z akce"
NEW_DEFAULT_SUBJECT = "Jaký to bylo? Zpětná vazba z akce *|nazev_akce|*"


def rename_variables(apps, schema_editor):
    FeedbackForm = apps.get_model("feedback", "FeedbackForm")
    for form in FeedbackForm.objects.exclude(email_content=""):
        content = form.email_content
        for old, new in RENAMES.items():
            content = content.replace(old, new)
        if content != form.email_content:
            form.email_content = content
            form.save(update_fields=["email_content"])
    FeedbackForm.objects.filter(email_subject=OLD_DEFAULT_SUBJECT).update(
        email_subject=NEW_DEFAULT_SUBJECT
    )


def revert_variables(apps, schema_editor):
    FeedbackForm = apps.get_model("feedback", "FeedbackForm")
    for form in FeedbackForm.objects.exclude(email_content=""):
        content = form.email_content
        for old, new in RENAMES.items():
            content = content.replace(new, old)
        if content != form.email_content:
            form.email_content = content
            form.save(update_fields=["email_content"])
    FeedbackForm.objects.filter(email_subject=NEW_DEFAULT_SUBJECT).update(
        email_subject=OLD_DEFAULT_SUBJECT
    )


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0018_fill_default_email_subject_and_content"),
    ]

    operations = [
        migrations.RunPython(rename_variables, revert_variables),
    ]
