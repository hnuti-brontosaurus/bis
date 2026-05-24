from itertools import chain

from bis.models import User
from dateutil.relativedelta import relativedelta
from django.utils import timezone

AGE_BUCKETS = [
    ("Nezletilí (0-17)", 0, 17),
    ("Mládež (0-26)", 0, 26),
    ("Středoškoláci (15-20)", 15, 20),
    ("Do 6 let", 0, 6),
    ("7 až 15 let", 7, 15),
    ("16 až 18 let", 16, 18),
    ("19 až 26 let", 19, 26),
    ("27 a více let", 27, 200),
]


def _age_tags(user: User) -> list[str]:
    if user.age is None:
        return ["Bez data narození"]
    if user.age < 0:
        return []
    return [name for name, low, high in AGE_BUCKETS if low <= user.age <= high]


def _activity_tags(user: User, today) -> list[str]:
    events = chain(
        user.events_where_was_as_main_organizer.all(),
        user.events_where_was_organizer.all(),
        (record.event for record in user.participated_in_events.all()),
    )
    starts = {event.id: event.start for event in events}.values()
    if not starts:
        return ["Bez akcí"]
    one_year_ago = today - relativedelta(years=1)
    two_years_ago = today - relativedelta(years=2)
    last_year_count = sum(1 for start in starts if start >= one_year_ago)
    if last_year_count > 2:
        return ["Aktivní"]
    if max(starts) < two_years_ago:
        return ["Rip"]
    return ["Spáči"]


def _membership_tags(user: User, today) -> list[str]:
    years = {m.year for m in user.memberships.all()}
    tags = []
    if today.year in years or today.year - 1 in years:
        tags.append("Aktivní člen")
    if today.year - 1 in years and today.year not in years:
        tags.append("Končící členství")
    if not tags:
        tags.append("Bez členství")
    return tags


def _organizer_tags(user: User, today) -> list[str]:
    one_year_ago = today - relativedelta(years=1)
    tags = []
    if any(
        e.start >= one_year_ago for e in user.events_where_was_as_main_organizer.all()
    ):
        tags.append("Aktivní hlavní organizátor")
    if any(e.start >= one_year_ago for e in user.events_where_was_organizer.all()):
        tags.append("Aktivní organizátor")
    return tags


def _qualification_tags(user: User, today) -> list[str]:
    tags = [
        q.category.name
        for q in user.qualifications.all()
        if q.valid_since <= today <= q.valid_till
    ]
    if not tags:
        tags.append("Bez kvalifikace")
    return tags


def _region_tags(user: User) -> list[str]:
    address = getattr(user, "address", None)
    if address and address.region:
        return [address.region.name]
    return []


def compute_tags(user: User) -> list[str]:
    today = timezone.now().date()
    tags = [role.name for role in user.roles.all()]
    tags.extend(_age_tags(user))
    tags.extend(_activity_tags(user, today))
    tags.extend(_membership_tags(user, today))
    tags.extend(_organizer_tags(user, today))
    tags.extend(_qualification_tags(user, today))
    tags.extend(_region_tags(user))
    if hasattr(user, "donor"):
        tags.append("Dárce")
    return tags
