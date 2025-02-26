from datetime import timedelta

from django.apps import apps
from django.utils.safestring import mark_safe


def record_history(history: dict, date, user, position):
    if not user:
        return
    user_id = str(user.id)
    date_ranges = history.setdefault(position, {}).setdefault(user_id, [])
    for range in date_ranges:
        if range[1] == str(date - timedelta(days=1)):
            range[1] = str(date)
            break
        if range[1] == str(date):
            return
    else:
        date_ranges.append([str(date), str(date)])


def show_history(history: dict):
    result = []
    user_map = {}
    User = apps.get_model("bis", "User")
    for position, position_data in history.items():
        for user_id, user_data in position_data.items():
            if user_id not in user_map:
                user_map[user_id] = User.objects.filter(id=user_id).first() or user_id
            user = user_map[user_id]

            for interval in user_data:
                result.append([position, user, interval])

    result.sort(key=lambda x: x[2][1], reverse=True)

    rows = "".join(
        [
            f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2][0]} - {row[2][1]}</td></tr>"
            for row in result
        ]
    )

    return mark_safe(f"<table>{rows}</table>")
