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


def make_donor(email, pledged_years_ago):
    user = User.objects.create(
        email=email, first_name="Test", last_name="Donor", _str="Test Donor"
    )
    donor = Donor.objects.create(user=user)
    donation_source, _ = DonationSourceCategory.objects.get_or_create(
        _import_id="1234567", name="Darujme", slug="darujme"
    )
    Pledge.objects.create(
        id=abs(hash(email)) % 10**8,
        donor=donor,
        donation_source=donation_source,
        is_recurrent=True,
        recurrent_state=RecurrentState.COLLECTING,
        pledged_at=timezone.now().date() - relativedelta(years=pledged_years_ago),
    )
    return donor


@pytest.fixture(autouse=True)
def automatic_email_setup(db):
    for year in range(1, 6):
        DonorEventCategory.objects.get_or_create(
            slug=f"pledge_{year}y",
            defaults={"description": f"Pravidelný dárce daruje již {year} let."},
        )
    FundraisingCampaign.objects.get_or_create(
        slug="automatic_emails", defaults={"name": "Automatické emaily"}
    )


@pytest.fixture
def sent_emails(monkeypatch):
    import bis.emails as emails_module

    calls = []
    monkeypatch.setattr(
        emails_module.ecomail,
        "send_email",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    return calls


def donor_event_slugs(donor):
    return set(
        DonorEvent.objects.filter(donor=donor).values_list(
            "event_type__slug", flat=True
        )
    )


@pytest.mark.django_db
def test_donor_without_events_gets_exactly_one_milestone_email(sent_emails):
    donor = make_donor("fresh@example.com", pledged_years_ago=3)

    donates_for_years()

    # The 3-year milestone fires once; the newly created pledge_3y event then
    # excludes the donor from the 2-year and 1-year iterations.
    assert donor_event_slugs(donor) == {"pledge_3y"}
    assert len(sent_emails) == 1
    assert sent_emails[0][0][1] == 174
    assert sent_emails[0][1]["variables"]["year"] == 3


@pytest.mark.django_db
def test_existing_lower_milestone_does_not_block_next_milestone(sent_emails):
    # Prod donor 1545 scenario: pledge_2y event exists, pledge is 3 years old,
    # so the 3-year milestone must still fire.
    donor = make_donor("lower@example.com", pledged_years_ago=3)
    DonorEvent.objects.create(
        donor=donor,
        event_type=DonorEventCategory.objects.get(slug="pledge_2y"),
        campaign=FundraisingCampaign.objects.get(slug="automatic_emails"),
    )

    donates_for_years()

    assert donor_event_slugs(donor) == {"pledge_2y", "pledge_3y"}
    assert len(sent_emails) == 1
    assert sent_emails[0][1]["variables"]["year"] == 3


@pytest.mark.django_db
def test_donor_with_current_milestone_is_not_renotified(sent_emails):
    donor = make_donor("current@example.com", pledged_years_ago=3)
    DonorEvent.objects.create(
        donor=donor,
        event_type=DonorEventCategory.objects.get(slug="pledge_3y"),
        campaign=FundraisingCampaign.objects.get(slug="automatic_emails"),
    )

    donates_for_years()

    # The existing pledge_3y excludes the donor from every iteration —
    # 3 >= 5 is false, and for the lower tiers 3 >= 2 and 3 >= 1 hold.
    assert donor_event_slugs(donor) == {"pledge_3y"}
    assert sent_emails == []


@pytest.mark.django_db
def test_five_year_donor_with_pledge_5y_event_gets_nothing(sent_emails):
    donor = make_donor("veteran@example.com", pledged_years_ago=5)
    DonorEvent.objects.create(
        donor=donor,
        event_type=DonorEventCategory.objects.get(slug="pledge_5y"),
        campaign=FundraisingCampaign.objects.get(slug="automatic_emails"),
    )

    donates_for_years()

    assert donor_event_slugs(donor) == {"pledge_5y"}
    assert sent_emails == []
