from datetime import timedelta

import pytest
from bis.models import User
from categories.models import DonorEventCategory, RoleCategory
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from donations.models import Donor, DonorEvent, FundraisingCampaign
from donations.telesales import get_reminders_due, get_worklist

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def categories(db):
    slugs = [
        "added_to_campaign",
        "call_no_answer",
        "call_declined",
        "call_postponed",
        "call_reached",
    ]
    return {
        slug: DonorEventCategory.objects.get_or_create(
            slug=slug, defaults={"description": slug}
        )[0]
        for slug in slugs
    }


@pytest.fixture
def campaign(db):
    return FundraisingCampaign.objects.create(name="Test", slug="test-worklist")


@pytest.fixture
def fundraiser_role(db):
    return RoleCategory.objects.get_or_create(
        slug="fundraiser", defaults={"name": "Fundraiser"}
    )[0]


@pytest.fixture
def board_member_role(db):
    return RoleCategory.objects.get_or_create(
        slug="board_member", defaults={"name": "Board member"}
    )[0]


def make_user(email, first_name="Test", last_name="User"):
    return User.objects.create(
        email=email,
        first_name=first_name,
        last_name=last_name,
        _str=f"{first_name} {last_name}",
    )


def make_fundraiser(email, fundraiser_role, first_name="Fundraiser", last_name="User"):
    user = make_user(email, first_name, last_name)
    user.roles.add(fundraiser_role)
    return user


def make_donor(user):
    return Donor.objects.create(user=user)


def add_to_campaign(donor, campaign, categories, created_at=None):
    event = DonorEvent.objects.create(
        donor=donor,
        event_type=categories["added_to_campaign"],
        campaign=campaign,
    )
    if created_at:
        DonorEvent.objects.filter(pk=event.pk).update(created_at=created_at)
    return event


def log_call(donor, campaign, categories, slug, created_at=None, reminder=None):
    event = DonorEvent.objects.create(
        donor=donor,
        event_type=categories[slug],
        campaign=campaign,
        reminder=reminder,
    )
    if created_at:
        DonorEvent.objects.filter(pk=event.pk).update(created_at=created_at)
    return event


# ---------------------------------------------------------------------------
# Query tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_worklist_excludes_donors_with_4_calls(categories, campaign):
    donor = make_donor(make_user("donor4@example.com"))
    add_to_campaign(donor, campaign, categories)

    now = timezone.now()
    for _ in range(4):
        log_call(donor, campaign, categories, "call_no_answer", created_at=now)

    assert donor not in list(get_worklist(campaign))


@pytest.mark.django_db
def test_worklist_includes_donor_with_3_calls(categories, campaign):
    donor = make_donor(make_user("donor3@example.com"))
    add_to_campaign(donor, campaign, categories)

    now = timezone.now()
    for _ in range(3):
        log_call(donor, campaign, categories, "call_no_answer", created_at=now)

    assert donor in list(get_worklist(campaign))


@pytest.mark.django_db
def test_postponed_reminder_resets_window(categories, campaign):
    donor = make_donor(make_user("donor_postponed@example.com"))

    base_time = timezone.now() - timedelta(days=10)
    add_to_campaign(donor, campaign, categories, created_at=base_time)

    for i in range(4):
        log_call(
            donor,
            campaign,
            categories,
            "call_no_answer",
            created_at=base_time + timedelta(hours=i + 1),
        )

    now = timezone.now()
    assert donor not in list(get_worklist(campaign))

    # Log postponement after the 4 old calls — window resets
    reminder_event_time = base_time + timedelta(days=5)
    reminder_due = now - timedelta(hours=1)
    log_call(
        donor,
        campaign,
        categories,
        "call_postponed",
        created_at=reminder_event_time,
        reminder=reminder_due,
    )

    reminders = list(get_reminders_due(campaign))
    assert donor in reminders

    # Making a call after the postponement moves donor out of reminders into worklist
    log_call(donor, campaign, categories, "call_no_answer", created_at=now)
    assert donor not in list(get_reminders_due(campaign))
    assert donor in list(get_worklist(campaign))


@pytest.mark.django_db
def test_reminders_due_surfaces_overdue_reminders(categories, campaign):
    donor = make_donor(make_user("donor_reminder@example.com"))

    past = timezone.now() - timedelta(days=5)
    add_to_campaign(donor, campaign, categories, created_at=past)
    reminder_due = timezone.now() - timedelta(hours=1)
    log_call(
        donor,
        campaign,
        categories,
        "call_postponed",
        created_at=past + timedelta(hours=1),
        reminder=reminder_due,
    )

    assert donor in list(get_reminders_due(campaign))


@pytest.mark.django_db
def test_future_reminder_appears_in_reminders_not_worklist(categories, campaign):
    donor = make_donor(make_user("donor_future_reminder@example.com"))

    past = timezone.now() - timedelta(days=2)
    add_to_campaign(donor, campaign, categories, created_at=past)
    future_reminder = timezone.now() + timedelta(days=1)
    log_call(
        donor,
        campaign,
        categories,
        "call_postponed",
        created_at=past + timedelta(hours=1),
        reminder=future_reminder,
    )

    assert donor in list(get_reminders_due(campaign))
    assert donor not in list(get_worklist(campaign))


@pytest.mark.django_db
def test_donor_with_reminder_goes_to_reminders_not_worklist(categories, campaign):
    donor = make_donor(make_user("donor_reminder2@example.com"))

    past = timezone.now() - timedelta(days=2)
    add_to_campaign(donor, campaign, categories, created_at=past)
    future_reminder = timezone.now() + timedelta(days=1)
    log_call(
        donor,
        campaign,
        categories,
        "call_postponed",
        created_at=timezone.now() - timedelta(minutes=30),
        reminder=future_reminder,
    )

    assert donor in list(get_reminders_due(campaign))
    assert donor not in list(get_worklist(campaign))


@pytest.mark.django_db
def test_call_declined_counts_toward_cap(categories, campaign):
    donor = make_donor(make_user("donor_declined@example.com"))
    add_to_campaign(donor, campaign, categories)

    now = timezone.now()
    for _ in range(3):
        log_call(donor, campaign, categories, "call_no_answer", created_at=now)
    log_call(donor, campaign, categories, "call_declined", created_at=now)

    assert donor not in list(get_worklist(campaign))


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_call_form_rejects_postponed_without_reminder(
    categories, campaign, fundraiser_role
):
    caller = make_fundraiser("fr1@example.com", fundraiser_role)
    donor = make_donor(make_user("donor_form@example.com"))

    client = Client()
    client.force_login(caller)

    url = reverse("admin:donations_telesales_call", args=[campaign.id, donor.id])
    response = client.post(
        url,
        {"outcome": "call_postponed", "fundraisers_note": "", "pledge": ""},
    )

    assert response.status_code == 200
    assert "Připomenutí je povinné".encode() in response.content


@pytest.mark.django_db
def test_call_form_rejects_postponed_with_past_reminder(
    categories, campaign, fundraiser_role
):
    caller = make_fundraiser("fr2@example.com", fundraiser_role)
    donor = make_donor(make_user("donor_form2@example.com"))

    client = Client()
    client.force_login(caller)

    past = (timezone.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
    url = reverse("admin:donations_telesales_call", args=[campaign.id, donor.id])
    response = client.post(
        url,
        {
            "outcome": "call_postponed",
            "fundraisers_note": "",
            "pledge": "",
            "reminder": past,
        },
    )

    assert response.status_code == 200
    assert b"budoucnosti" in response.content


@pytest.mark.django_db
def test_non_fundraiser_gets_403(categories, campaign, board_member_role):
    non_fundraiser = make_user("regular@example.com")
    non_fundraiser.roles.add(board_member_role)  # is_staff=True but not fundraiser

    client = Client()
    client.force_login(non_fundraiser)

    url = reverse("admin:donations_telesales_worklist", args=[campaign.id])
    response = client.get(url)
    assert response.status_code == 403

    url_call = reverse("admin:donations_telesales_call", args=[campaign.id, 99999])
    response_call = client.get(url_call)
    assert response_call.status_code == 403


@pytest.mark.django_db
def test_fundraiser_can_see_donors_in_worklist(categories, campaign):
    donor = make_donor(make_user("donor_vis@example.com"))
    add_to_campaign(donor, campaign, categories)

    assert donor in list(get_worklist(campaign))
