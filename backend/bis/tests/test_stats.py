from datetime import date

import pytest
from administration_units.models import AdministrationUnit
from bis.helpers import AgeStats, MembershipStats, paused_validation
from bis.models import Membership, User
from categories.models import AdministrationUnitCategory, MembershipCategory
from django.db.models import Min


@pytest.mark.django_db
def test_age_stats_count_whole_years_at_the_date():
    for birthday in (
        date(2000, 1, 1),  # 26 on the day itself
        date(2000, 1, 2),  # 25 for one more day
        date(2027, 6, 1),
        None,
    ):
        User.objects.create(birthday=birthday)

    stats = AgeStats("lidí", User.objects.all(), date(2026, 1, 1))

    assert stats.total == 4
    assert stats.unborn == 1
    assert stats.without_birthday == 1
    assert stats.birthdays_stats == {25: 1, 26: 1}
    assert stats.oldest == 26


@pytest.fixture
def unit(db):
    # AdministrationUnit.clean() wants a manager, which these stats ignore
    with paused_validation():
        return AdministrationUnit.objects.create(
            name="Článek",
            abbreviation="CL",
            is_for_kids=False,
            email="clanek@example.com",
            category=AdministrationUnitCategory.objects.create(
                name="Základní článek", slug="basic_section"
            ),
        )


def test_age_stats_count_the_rows_the_queryset_returns(unit):
    category = MembershipCategory.objects.create(name="Dospělý", slug="adult")
    user = User.objects.create(birthday=date(2000, 6, 1))
    for year in (2024, 2025):
        Membership.objects.create(
            user=user, category=category, administration_unit=unit, year=year
        )
    members = User.objects.filter(memberships__category=category)

    def total(queryset):
        return AgeStats("", queryset, date(2026, 1, 1)).total

    assert total(members) == 2
    assert total(members.distinct()) == 1
    assert total(User.objects.annotate(first=Min("memberships__year"))) == 1


def test_membership_stats_sum_prices_per_category(unit):
    adult = MembershipCategory.objects.create(name="Dospělý", slug="adult")
    kid = MembershipCategory.objects.create(name="Dítě", slug="kid")
    for category in (adult, adult, kid):
        Membership.objects.create(
            user=User.objects.create(),
            category=category,
            administration_unit=unit,
            year=2025,
        )

    stats = MembershipStats("", Membership.objects.all())

    assert stats.get_data() == {
        "Dospělý": "900 Kč (2x)",
        "Dítě": "250 Kč (1x)",
        "Celkem": "1150 Kč",
    }
