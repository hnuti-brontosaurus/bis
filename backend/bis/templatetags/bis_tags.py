from administration_units.models import AdministrationUnit
from bis.admin_filters import EventStatsDateFilter, UserStatsDateFilter
from bis.helpers import AgeStats, MembershipStats
from bis.models import Membership, User
from django import template
from django.contrib.admin.templatetags.admin_list import date_hierarchy
from django.contrib.admin.templatetags.base import InclusionAdminNode
from django.utils.datetime_safe import date
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from event.models import Event
from other.models import DashboardItem

register = template.Library()


@register.simple_tag(takes_context=True)
def user_stats(context, changelist):
    queryset = changelist.queryset
    stats = []
    request = context["request"]
    to_date = date(now().year, 1, 1)
    if queryset.model is User:
        selected_date = getattr(request, UserStatsDateFilter.cache_name, None)
        if selected_date:
            to_date = selected_date["chairman_of__existed_since"].date()

        stats.append(AgeStats("lidí", queryset, to_date))

        year = date.today().year
        header = f"{queryset.count()} lidí"
        membership_stats_query = getattr(request, "membership_stats_query", {})
        if not membership_stats_query:
            membership_stats_query = dict(year=year)

        membership_stats_query["user__in"] = queryset

        if year := membership_stats_query.get("year"):
            header += f" za rok {year}"
        if year := membership_stats_query.get("year__gte"):
            header += f" od roku {year}"
        if year := membership_stats_query.get("year__lte"):
            header += f" do roku {year}"
        if administration_unit := membership_stats_query.get("administration_unit"):
            header += f" organizační jednotky {AdministrationUnit.objects.get(id=administration_unit).abbreviation}"

        stats.append(
            MembershipStats(header, Membership.objects.filter(**membership_stats_query))
        )

    if queryset.model is Membership:
        year = request.GET.get("_year__year") or date.today().year
        stats.append(MembershipStats(f"za rok {year}", queryset.filter(year=year)))

    event_stats_date = getattr(request, EventStatsDateFilter.cache_name, None)
    if queryset.model is Event and event_stats_date:
        to_date = event_stats_date["main_organizer__birthday"].date()
        user_queryset = User.objects.filter(participated_in_events__event__in=queryset)
        stats.append(AgeStats("účastí na akci", user_queryset, to_date))
        user_queryset = user_queryset.distinct()
        stats.append(AgeStats("unikátních účastí na akci", user_queryset, to_date))

        user_queryset = User.objects.filter(events_where_was_organizer__in=queryset)
        stats.append(AgeStats("zorganizování akce", user_queryset, to_date))
        user_queryset = user_queryset.distinct()
        stats.append(AgeStats("unikátních zorganizování akce", user_queryset, to_date))

    return mark_safe("".join([stat.as_table() for stat in stats]))


@register.simple_tag(takes_context=True)
def user_dashboard(context, user):
    items = DashboardItem.get_items_for_user(user)

    result = ""
    for item in items:
        result += f'<li>{item.date.day}. {item.date.month}. {item.date.year}: {item.name}<br><span class="mini quiet">{item.description}</span></li>'

    return mark_safe(f"<ul>{result}</ul>")


def membership_date_hierarchy(cl):
    queryset = cl.queryset
    cl.queryset = Membership.objects.all()
    result = date_hierarchy(cl)
    if result["back"] is None:
        result["title"] = "Zobrazit členství jen za rok:"
    else:
        year = cl.params.get("_year__year")
        result["choices"] = []
        result["title"] = f"Zobrazuji členství za rok {year}"
        result["back"]["title"] = "zobrazit všechna"

    cl.queryset = queryset
    return result


@register.tag(name="membership_date_hierarchy")
def membership_date_hierarchy_tag(parser, token):
    return InclusionAdminNode(
        parser,
        token,
        func=membership_date_hierarchy,
        template_name="membership_date_hierarchy.html",
        takes_context=False,
    )
