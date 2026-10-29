import datetime

import pytest
from administration_units.models import AdministrationUnit
from bis.admin import DonorAdminInline
from bis.models import Membership, User
from categories.models import (
    AdministrationUnitCategory,
    DonationSourceCategory,
    DonorEventCategory,
    MembershipCategory,
    RoleCategory,
)
from django.contrib.admin.sites import site
from django.test import Client, RequestFactory
from django.urls import reverse
from donations.models import Donation, Donor, DonorEvent, FundraisingCampaign


def make_user(email):
    return User.objects.create(email=email, first_name=email, last_name="Test")


@pytest.fixture
def unit(db):
    chairman = make_user("chairman@example.com")
    return AdministrationUnit.objects.create(
        name="Článek",
        abbreviation="CL",
        is_for_kids=False,
        email="clanek@example.com",
        category=AdministrationUnitCategory.objects.create(
            name="Základní článek", slug="basic_section"
        ),
        chairman=chairman,
        manager=chairman,
    )


@pytest.fixture
def board_member(unit):
    user = make_user("board@example.com")
    unit.board_members.add(user)
    user.can_see_all = False
    user.is_board_member = True
    return user


@pytest.fixture
def superuser(db):
    user = make_user("admin@example.com")
    user.roles.add(RoleCategory.objects.get_or_create(slug="admin")[0])
    return user


def make_donor(email, amounts, **kwargs):
    donor = Donor.objects.create(user=make_user(email), **kwargs)
    source, _ = DonationSourceCategory.objects.get_or_create(
        slug="darujme", defaults={"name": "Darujme"}
    )
    for month, amount in enumerate(amounts, start=1):
        Donation.objects.create(
            donor=donor,
            donated_at=datetime.date(2026, month, 1),
            amount=amount,
            donation_source=source,
        )
    return donor


def make_member(user, unit):
    category, _ = MembershipCategory.objects.get_or_create(
        slug="adult", defaults={"name": "Dospělý"}
    )
    Membership.objects.create(user=user, category=category, administration_unit=unit)


def listed_users(viewer, params):
    request = RequestFactory().get("/admin/bis/user/", params)
    request.user = viewer
    changelist = site._registry[User].get_changelist_instance(request)
    return set(changelist.get_queryset(request))


def test_donor_filters_see_only_visible_donors(unit, board_member):
    supporter = make_donor("supporter@example.com", [600], basic_section_support=unit)
    member = make_donor("member@example.com", [600]).user
    make_member(member, unit)

    assert member in listed_users(board_member, {})
    assert listed_users(board_member, {"donations_sum_from": "500"}) == {supporter.user}
    assert listed_users(board_member, {"is_donor": "yes"}) == {supporter.user}


def test_donation_sum_follows_the_date_range(superuser):
    make_donor("early@example.com", [600])
    late = make_donor("late@example.com", [100, 100, 600])

    users = listed_users(
        superuser,
        {"donated_at__range__gte": "2026-02-01", "donations_sum_from": "500"},
    )

    assert users == {late.user}


def test_campaign_filters_see_only_visible_donors(unit, board_member):
    campaign = FundraisingCampaign.objects.create(name="Kampaň", slug="kampan")
    event_type = DonorEventCategory.objects.create(description="Volat", slug="test")
    supporter = make_donor("supporter@example.com", [], basic_section_support=unit)
    member = make_user("member@example.com")
    make_member(member, unit)
    for user in [supporter.user, member]:
        DonorEvent.objects.create(user=user, campaign=campaign, event_type=event_type)

    params = {"campaign_events__campaign__id__in": str(campaign.id)}

    assert member in listed_users(board_member, {})
    assert listed_users(board_member, params) == {supporter.user}


def test_user_list_renders_with_donor_filters(superuser):
    make_donor("donor@example.com", [600])
    client = Client()
    client.force_login(superuser)

    response = client.get(
        reverse("admin:bis_user_changelist"),
        {
            "columns": "donor",
            "is_donor": "yes",
            "has_recurrent_donation_filter": "no",
            "is_public__exact": "1",
            "first_donation__range__gte": "2026-01-01",
            "reccuring_donor_who_stopped": "yes",
        },
    )

    assert response.status_code == 200
    assert response.context["cl"].result_count == 0


def test_donor_is_edited_on_the_user(superuser):
    donor = make_donor("donor@example.com", [600])
    client = Client()
    client.force_login(superuser)

    response = client.get(reverse("admin:bis_user_change", args=[donor.user.id]))

    assert response.status_code == 200
    assert b"_donation_confirmation_pdf_export" in response.content
    assert DonorAdminInline in response.context["adminform"].model_admin.get_inlines(
        response.wsgi_request, donor.user
    )


def test_old_donor_links_lead_to_the_user(superuser):
    donor = make_donor("donor@example.com", [])
    client = Client()
    client.force_login(superuser)

    response = client.get(reverse("admin:donations_donor_change", args=[donor.id]))

    assert response.url == reverse("admin:bis_user_change", args=[donor.user.id])
