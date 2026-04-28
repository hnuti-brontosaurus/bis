from django.db import migrations, models


def copy_subscribed_to_status(apps, schema_editor):
    User = apps.get_model("bis", "User")
    User.objects.filter(subscribed_to_newsletter=False).update(subscription_status=2)


def copy_status_to_subscribed(apps, schema_editor):
    User = apps.get_model("bis", "User")
    User.objects.filter(subscription_status=1).update(subscribed_to_newsletter=True)
    User.objects.exclude(subscription_status=1).update(subscribed_to_newsletter=False)


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0055_rename_internal_note_event_organizers_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="subscription_status",
            field=models.IntegerField(
                choices=[(1, "Odebírá"), (2, "Neodebírá"), (4, "Nedoručitelný")],
                default=1,
            ),
        ),
        migrations.RunPython(
            copy_subscribed_to_status,
            reverse_code=copy_status_to_subscribed,
        ),
        migrations.RemoveField(
            model_name="user",
            name="subscribed_to_newsletter",
        ),
    ]
