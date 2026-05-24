import re

from django.db import migrations

REPAIRS = [
    (re.compile(r"^([^,]+),.+$"), r"\1"),  # take first email before comma
    (re.compile(r"\s+"), ""),  # strip whitespace
    (re.compile(r"\.+@"), "@"),  # strip dots before @
    (re.compile(r"@([^@]*?)\.{2,}"), r"@\1."),  # collapse double dots in domain
    (re.compile(r"\.comj$", re.IGNORECASE), ".com"),
    (re.compile(r"\.comm$", re.IGNORECASE), ".com"),
    (re.compile(r"\.ocm$", re.IGNORECASE), ".com"),
    (re.compile(r"@sznam\.cz$", re.IGNORECASE), "@seznam.cz"),
]
NULLIFY = re.compile(
    r"^(?:[^@]*|.*@[^.]+\.[a-z]|.*@gk\.zy)$",
    re.IGNORECASE,
)


def repair_email(email):
    for pattern, replacement in REPAIRS:
        email = pattern.sub(replacement, email)
    if NULLIFY.match(email):
        return None
    return email


def cleanup(apps, schema_editor):
    from bis.models import User as RealUser

    User = apps.get_model("bis", "User")
    UserEmail = apps.get_model("bis", "UserEmail")

    rows = list(
        User.objects.filter(email__isnull=False).values_list("id", "email"),
    )
    for user_id, email in rows:
        repaired = repair_email(email)
        if repaired == email:
            continue

        UserEmail.objects.filter(user_id=user_id, email=email).delete()
        User.objects.filter(id=user_id).update(email=None)

        if repaired is None:
            continue

        other_id = (
            User.objects.filter(email=repaired)
            .exclude(id=user_id)
            .values_list("id", flat=True)
            .first()
        )
        if other_id is not None:
            RealUser.objects.get(id=other_id).merge_with(
                RealUser.objects.get(id=user_id)
            )
            continue

        max_order = (
            UserEmail.objects.filter(user_id=user_id)
            .order_by("-order")
            .values_list("order", flat=True)
            .first()
            or 0
        )
        UserEmail.objects.create(user_id=user_id, email=repaired, order=max_order + 1)
        User.objects.filter(id=user_id).update(email=repaired)


class Migration(migrations.Migration):
    dependencies = [
        ("bis", "0058_merge_event_organizers_note"),
    ]

    operations = [migrations.RunPython(cleanup, migrations.RunPython.noop)]
