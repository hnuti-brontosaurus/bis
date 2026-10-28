import datetime

import pytest
from administration_units.models import AdministrationUnit
from bis.admin import annotate_visible_donor_stats
from bis.models import User
from categories.models import AdministrationUnitCategory, DonationSourceCategory
from django.contrib.admin.sites import site
from django.test import RequestFactory
from donations.models import Donation, Donor, Pledge

BASIC_COLUMNS = ["get_name", "get_links", "birthday", "address", "email", "phone"]


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


def make_donor(email, **kwargs):
    donor = Donor.objects.create(user=make_user(email), **kwargs)
    source, _ = DonationSourceCategory.objects.get_or_create(
        slug="darujme", defaults={"name": "Darujme"}
    )
    for month, amount in [(1, 100), (3, 500)]:
        Donation.objects.create(
            donor=donor,
            donated_at=datetime.date(2026, month, 1),
            amount=amount,
            donation_source=source,
        )
    return donor


@pytest.fixture
def board_member(unit):
    user = make_user("board@example.com")
    unit.board_members.add(user)
    user.can_see_all = False
    user.is_board_member = True
    return user


def list_display(columns, user):
    request = RequestFactory().get("/admin/bis/user/", {"columns": columns})
    request.user = user
    return site._registry[User].get_list_display(request)


@pytest.mark.parametrize(
    "columns, extra",
    [
        ("", []),
        ("organizer", ["get_qualifications", "get_memberships"]),
        (
            "donor",
            [
                "get_donations_sum",
                "get_last_donation",
                "get_has_active_recurrent_donation",
            ],
        ),
    ],
)
def test_preset_adds_its_columns(db, columns, extra):
    assert list_display(columns, make_user("viewer@example.com")) == [
        *BASIC_COLUMNS,
        *extra,
    ]


def test_donor_stats_are_shown_only_for_visible_donors(unit, board_member):
    supporter = make_donor("supporter@example.com", basic_section_support=unit)
    Pledge.objects.create(
        id=1,
        donor=supporter,
        donation_source=DonationSourceCategory.objects.get(slug="darujme"),
        is_recurrent=True,
        recurrent_state="collecting",
        pledged_at=datetime.date(2026, 1, 1),
    )
    stranger = make_donor("stranger@example.com")
    nobody = make_user("nobody@example.com")

    users = annotate_visible_donor_stats(User.objects.all(), board_member)
    stats = {
        user.pk: (
            user.donations_sum,
            user.last_donation,
            user.has_active_recurrent_donation,
        )
        for user in users
    }

    assert stats[supporter.user.pk] == (600, datetime.date(2026, 3, 1), True)
    assert stats[stranger.user.pk] == (None, None, None)
    assert stats[nobody.pk] == (None, None, None)
