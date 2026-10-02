from datetime import date

from admin_auto_filters.filters import AutocompleteFilter
from administration_units.models import AdministrationUnit
from bis.admin_filters import EventStatsDateFilter, UserStatsDateFilter
from bis.admin_helpers import FilterGroupTitle
from bis.helpers import AgeStats, MembershipStats
from bis.models import Membership, User
from django import template
from django.contrib.admin.templatetags.admin_list import date_hierarchy
from django.contrib.admin.templatetags.base import InclusionAdminNode
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


def used_parameters(changelist, spec):
    return {
        parameter: values
        for parameter in spec.expected_parameters() or ()
        if any(values := changelist.filter_params.get(parameter, ()))
    }


@register.simple_tag
def filter_groups(changelist):
    groups = [{"title": None, "filters": []}]
    for spec in changelist.filter_specs:
        if isinstance(spec, FilterGroupTitle):
            groups.append(
                {"title": spec.title, "collapsed": spec.collapsed, "filters": []}
            )
        else:
            groups[-1]["filters"].append(
                {"spec": spec, "active": bool(used_parameters(changelist, spec))}
            )

    for group in groups:
        group["active_count"] = sum(item["active"] for item in group["filters"])
    return groups


RANGE_BOUNDS = {"_from": "od", "__gte": "od", "_to": "do", "__lte": "do"}


def describe_filter_value(changelist, spec, parameters):
    bounds = [
        f"{word} {values[-1]}"
        for parameter, values in parameters.items()
        for suffix, word in RANGE_BOUNDS.items()
        if parameter.endswith(suffix) and values[-1]
    ]
    if bounds:
        return " ".join(bounds)

    if isinstance(spec, AutocompleteFilter):
        queryset = spec.get_queryset_for_field(
            spec.rel_model or changelist.model, spec.field_name
        )
        return ", ".join(
            str(item)
            for item in queryset.filter(pk__in=parameters[spec.parameter_name])
        )

    return ", ".join(
        str(choice["display"])
        for choice in spec.choices(changelist)
        if choice.get("selected")
    )


@register.simple_tag
def active_filters(changelist):
    return [
        {
            "title": spec.title,
            "value": describe_filter_value(changelist, spec, parameters),
            "remove_url": changelist.get_query_string(
                remove=spec.expected_parameters()
            ),
        }
        for spec in changelist.filter_specs
        if (parameters := used_parameters(changelist, spec))
    ]
