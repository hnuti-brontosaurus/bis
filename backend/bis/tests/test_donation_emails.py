import itertools

import pytest
from bis.emails import donates_for_years
from bis.models import User
from categories.models import DonationSourceCategory, DonorEventCategory
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from donations.models import (
    Donor,
    DonorEvent,
    FundraisingCampaign,
    Pledge,
    RecurrentState,
)

pledge_ids = itertools.count(1)


@pytest.fixture(autouse=True)
def categories(db):
    for year in range(1, 6):
        DonorEventCategory.objects.get_or_create(
            slug=f"pledge_{year}y", defaults={"description": f"{year}y"}
        )
    FundraisingCampaign.objects.get_or_create(
        slug="automatic_emails", defaults={"name": "Automatické emaily"}
    )


@pytest.fixture
def sent_emails(monkeypatch):
    from bis import emails

    sent = []
    monkeypatch.setattr(
        emails.ecomail,
        "send_email",
        lambda *args, variables, **kwargs: sent.append(variables["year"]),
    )
    return sent


def make_donor(pledged_years_ago, milestones=()):
    user = User.objects.create(email=f"{next(pledge_ids)}@example.com", _str="Donor")
    donor = Donor.objects.create(user=user)
    Pledge.objects.create(
        id=next(pledge_ids),
        donor=donor,
        donation_source=DonationSourceCategory.objects.get_or_create(
            slug="darujme", defaults={"name": "Darujme"}
        )[0],
        is_recurrent=True,
        recurrent_state=RecurrentState.COLLECTING,
        pledged_at=timezone.now().date() - relativedelta(years=pledged_years_ago),
    )
    for year in milestones:
        DonorEvent.objects.create(
            donor=donor,
            event_type=DonorEventCategory.objects.get(slug=f"pledge_{year}y"),
            campaign=FundraisingCampaign.objects.get(slug="automatic_emails"),
        )
    return donor


def milestones(donor):
    return set(donor.events.values_list("event_type__slug", flat=True))


def test_new_donor_gets_only_the_highest_milestone(sent_emails):
    donor = make_donor(pledged_years_ago=3)

    donates_for_years()

    assert sent_emails == [3]
    assert milestones(donor) == {"pledge_3y"}


def test_lower_milestone_does_not_block_the_next_one(sent_emails):
    donor = make_donor(pledged_years_ago=3, milestones=[2])

    donates_for_years()

    assert sent_emails == [3]
    assert milestones(donor) == {"pledge_2y", "pledge_3y"}


@pytest.mark.parametrize("reached", [3, 5])
def test_reached_milestone_is_not_repeated(sent_emails, reached):
    make_donor(pledged_years_ago=reached, milestones=[reached])

    donates_for_years()

    assert sent_emails == []
