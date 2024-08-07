import re
from collections import Counter
from functools import wraps
from time import time

from categories.models import MembershipCategory
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from unidecode import unidecode


class SearchMixin:
    search_fields = []

    @classmethod
    def get_search_fields(cls, prefix=""):
        return [prefix + f for f in cls.search_fields + ["_search_field"]]

    @classmethod
    def get_nested_attr(cls, obj, fields):
        if len(fields) == 0:
            return obj
        obj = getattr(obj, fields[0], None) or ""
        return cls.get_nested_attr(obj, fields[1:])

    def get_search_field_value(self):
        return " ".join(
            unidecode(str(self.get_nested_attr(self, field.split("__"))))
            for field in self.search_fields
        )[:1000]


def print_progress(name, i, total):
    key = f"progress_of_{slugify(name)}"

    if i >= total - 1:
        cache.set(key, None)
        return

    obj = cache.get(key)
    if not obj:
        print(name, flush=True)
        cache.set(key, time())

    elif time() - obj >= 1:
        print(f"{name}, progress {100 * i / total:.2f}%", flush=True)
        cache.set(key, time())


def cache_into_self(name):
    name = f"__cache__{name}"

    def decorator(f):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, name):
                return getattr(self, name)

            result = f(self, *args, **kwargs)

            setattr(self, name, result)

            return result

        return wrapper

    return decorator


def permission_cache(f):
    return cache_into_self("permission_cache")(f)


def update_roles(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            to_update = set()
            old = self._meta.model.objects.filter(id=self.id).first()
            if old:
                for role in roles:
                    to_update.add(getattr(old, role))

            f(self, *args, **kwargs)

            for role in roles:
                to_update.add(getattr(self, role))

            for user in to_update:
                if user:
                    user.update_roles()

        return wrapper

    return decorator


class paused_validation:
    def __enter__(self):
        self.validation_paused = not cache.get("skip_validation")
        if self.validation_paused:
            cache.set("skip_validation", True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.validation_paused:
            cache.set("skip_validation", False)


def with_paused_validation(f):
    def wrapper(*args, **kwargs):
        with paused_validation():
            return f(*args, **kwargs)

    return wrapper


class paused_emails:
    def __enter__(self):
        self.emails_paused = not cache.get("emails_paused")
        if self.emails_paused:
            cache.set("emails_paused", True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.emails_paused:
            cache.set("emails_paused", False)


def with_paused_emails(f):
    def wrapper(*args, **kwargs):
        with paused_emails():
            return f(*args, **kwargs)

    return wrapper


def on_save(fn, when="always"):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if when == "always":
                run_fn = True
            elif when == "on_create":
                run_fn = self._state.adding
            else:
                assert False, "Invalid when argument"

            f(self, *args, **kwargs)

            if run_fn:
                fn(self)

        return wrapper

    return decorator


class AgeStats:
    def __init__(self, header, queryset, date):
        self.date = date
        self.total = queryset.count()
        self.header = header

        birthdays = queryset.filter(birthday__isnull=False).values_list(
            "birthday", flat=True
        )
        ages = [relativedelta(date, birthday).years for birthday in birthdays]
        self.without_birthday = self.total - len(ages)
        self.unborn = len([age for age in ages if age < 0])

        ages = [age for age in ages if age >= 0]
        self.oldest = max(ages + [0])
        self.birthdays_stats = Counter(ages)

    def age_count(self, low, high):
        return sum(self.birthdays_stats.get(age, 0) for age in range(low, high + 1))

    def age_stats(self, low, high):
        return self.format_count(self.age_count(low, high))

    def format_count(self, count):
        if not count:
            return None
        alive = self.total - self.unborn
        if not alive:
            return count

        return f"{count} - {count / alive * 100:.1f}%"

    def get_header(self):
        return f"Statistika věku {self.total} {self.header} ke dni {self.date}"

    def get_data(self):
        data = {
            "celkem": self.total,
            "nenarození": self.unborn,
            "věk neznámý": self.format_count(self.without_birthday),
            "nezletilí (0-17)": self.age_stats(0, 17),
            "mládež (0-26)": self.age_stats(0, 26),
            "středoškoláci (15-20)": self.age_stats(15, 20),
            "do 6 let": self.age_stats(0, 6),
            "7 až 15 let": self.age_stats(7, 15),
            "16 až 18 let": self.age_stats(16, 18),
            "19 až 26 let": self.age_stats(19, 26),
            "27 a více let": self.age_stats(27, self.oldest),
        }
        return {key: str(value) for key, value in data.items() if value}

    def as_table(self):
        data = self.get_data()

        def make_cell(item):
            return f'<td>{item.replace(" - ", "<br>")}</td>'

        def make_row(items):
            return f'<tr>{"".join(make_cell(item) for item in items)}</tr>'

        header = f"<tr><th colspan={len(data)}>{self.get_header()}</th></tr>"

        return mark_safe(
            f"<table>"
            f"{header}"
            f"{make_row(data.keys())}"
            f"{make_row(data.values())}"
            f"</table>"
        )


class MembershipStats:
    def __init__(self, header, queryset):
        self.header = header
        self.queryset = queryset

    def get_header(self):
        return f"Sumarizace členských příspěvků {self.header}"

    def get_data(self):
        data = {
            category.name: [
                item.price
                for item in self.queryset.filter(category=category).select_related(
                    "category"
                )
            ]
            for category in MembershipCategory.objects.all()
        }
        total = sum(price for items in data.values() for price in items)
        data = {
            key: f"{sum(items)} Kč ({len(items)}x)"
            for key, items in data.items()
            if items
        }
        data["Celkem"] = f"{total} Kč"
        return data

    def as_table(self):
        data = self.get_data()

        def make_cell(item):
            return f'<td>{item.replace(" - ", "<br>")}</td>'

        def make_row(items):
            return f'<tr>{"".join(make_cell(item) for item in items)}</tr>'

        header = f"<tr><th colspan={len(data)}>{self.get_header()}</th></tr>"
        return mark_safe(
            f"<table>"
            f"{header}"
            f"{make_row(data.keys())}"
            f"{make_row(data.values())}"
            f"</table>"
        )


def to_snake_case(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def filter_queryset_with_multiple_or_queries(queryset, queries):
    ids = set()
    for query in queries:
        ids = ids.union(queryset.filter(query).order_by().values_list("id", flat=True))
    return queryset.filter(id__in=ids)


def get_locked_year():
    locked_year = today().year - 1
    if today().month < 3:
        locked_year -= 1

    return locked_year


def make_a(content, link):
    return mark_safe(f'<a href="{link}">{content}</a>')


def make_ul(data):
    data = "".join(f"<li>{item}</li>" for item in data)
    return mark_safe(f"<ul>{data}</ul>")


def make_br(data):
    return mark_safe("<br>".join(data))


def make_td(cell):
    return f"<td>{cell}</td>"


def make_th(cell):
    return f"<th>{cell}</th>"


def make_tr(row):
    row = "".join(make_td(cell) for cell in row)
    return f"<tr>{row}</tr>"


def make_table(data, header=""):
    header = "".join(make_th(cell) for cell in header)
    rows = "".join(make_tr(row) for row in data)
    return mark_safe(f"<table>{header}{rows}</table>")
