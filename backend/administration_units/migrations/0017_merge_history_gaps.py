from datetime import date

from django.db import migrations

MAX_MERGEABLE_GAP_DAYS = 31


def merge_history_gaps(history):
    changed = False
    for users in history.values():
        for user_id, ranges in users.items():
            ranges.sort(key=lambda r: r[0])
            merged = [ranges[0]]
            for start_str, end_str in ranges[1:]:
                prev_end = date.fromisoformat(merged[-1][1])
                cur_start = date.fromisoformat(start_str)
                gap_days = (cur_start - prev_end).days - 1
                if 0 <= gap_days <= MAX_MERGEABLE_GAP_DAYS:
                    if end_str > merged[-1][1]:
                        merged[-1][1] = end_str
                    changed = True
                else:
                    merged.append([start_str, end_str])
            users[user_id] = merged
    return changed


def forwards(apps, schema_editor):
    for model_name in (
        "AdministrationUnit",
        "AdministrationSubUnit",
        "BrontosaurusMovement",
    ):
        Model = apps.get_model("administration_units", model_name)
        to_update = [
            obj for obj in Model.objects.all() if merge_history_gaps(obj._history)
        ]
        if to_update:
            Model.objects.bulk_update(to_update, ["_history"])


class Migration(migrations.Migration):
    dependencies = [
        ("administration_units", "0016_brontosaurusmovement_fundraisers"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
