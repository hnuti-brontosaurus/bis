from datetime import date

from django.apps import apps
from django.utils.safestring import mark_safe

MAX_GAP_DAYS = 31


def record_history(history: dict, day, user, position):
    if not user:
        return
    user_id = str(user.id)
    date_ranges = history.setdefault(position, {}).setdefault(user_id, [])
    day_str = str(day)
    for date_range in date_ranges:
        if date_range[0] <= day_str <= date_range[1]:
            return
        gap = (day - date.fromisoformat(date_range[1])).days
        if 0 < gap <= MAX_GAP_DAYS:
            date_range[1] = day_str
            break
    else:
        date_ranges.append([day_str, day_str])


def show_history(history: dict):
    result = []
    user_map = {}
    User = apps.get_model("bis", "User")
    for position, position_data in history.items():
        for user_id, user_data in position_data.items():
            if user_id not in user_map:
                user_map[user_id] = User.objects.filter(id=user_id).first() or user_id
            user = user_map[user_id]

            result.extend([position, user, interval] for interval in user_data)

    result.sort(key=lambda x: x[2][1], reverse=True)

    rows = "".join(
        [
            f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2][0]} - {row[2][1]}</td></tr>"
            for row in result
        ]
    )

    return mark_safe(f"<table>{rows}</table>")
