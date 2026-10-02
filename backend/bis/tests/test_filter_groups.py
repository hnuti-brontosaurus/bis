from bis.models import User
from bis.templatetags.bis_tags import active_filters, filter_groups
from django.contrib.admin import site
from django.test import RequestFactory
from donations.models import Donor


def groups_for(params):
    request = RequestFactory().get("/admin/donations/donor/", params)
    request.user = User.objects.create(email="admin@example.com", _str="Admin")
    request.user.is_superuser = True
    changelist = site._registry[Donor].get_changelist_instance(request)
    return {group["title"]: group for group in filter_groups(changelist)}


def test_filters_are_grouped_under_their_title(db):
    groups = groups_for({})

    assert list(groups) == [None, "Kontaktování", "Dary", "Fundraisingové kampaně"]
    assert all(group["filters"] for group in groups.values())
    assert groups["Dary"]["collapsed"]
    assert not groups["Dary"]["active_count"]


def test_group_with_an_applied_filter_is_active(db):
    groups = groups_for({"donated_at__range__gte": "2026-01-01"})

    assert groups["Dary"]["active_count"] == 1
    assert not groups["Fundraisingové kampaně"]["active_count"]


def test_empty_filter_parameter_does_not_activate_group(db):
    groups = groups_for({"donated_at__range__gte": ""})

    assert not groups["Dary"]["active_count"]


def active_filters_for(model, params):
    request = RequestFactory().get("/", params)
    request.user = User.objects.create(email="admin@example.com", _str="Admin")
    request.user.is_superuser = True
    changelist = site._registry[model].get_changelist_instance(request)
    return {item["title"]: item for item in active_filters(changelist)}


def test_active_filters_describe_their_values(db):
    filters = active_filters_for(
        User, {"age_from": "18", "age_to": "", "birthday_set": "yes"}
    )

    assert filters["Věk"]["value"] == "od 18"
    assert filters["Datum narození vyplněno?"]["value"] == "Ano"
    assert list(filters) == ["Věk", "Datum narození vyplněno?"]


def test_removing_active_filter_drops_all_its_parameters(db):
    filters = active_filters_for(
        User, {"age_from": "18", "age_to": "", "birthday_set": "yes"}
    )

    assert filters["Věk"]["remove_url"] == "?birthday_set=yes"
