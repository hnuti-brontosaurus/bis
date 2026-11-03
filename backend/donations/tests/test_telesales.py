from datetime import timedelta

import pytest
from bis.models import User
from categories.models import (
    DonationSourceCategory,
    DonorEventCategory,
    RoleCategory,
)
from django.contrib.admin import helpers
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from donations.models import Donation, Donor, DonorEvent, FundraisingCampaign
from donations.telesales import get_finished, get_reminders_due, get_worklist
from ecomail.tags import GIFTLESS_DONOR_CUTOFF, compute_tags


@pytest.fixture
def categories(db):
    slugs = [
        "added_to_campaign",
        "call_no_answer",
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


@pytest.fixture
def education_member_role(db):
    return RoleCategory.objects.get_or_create(
        slug="education_member", defaults={"name": "Education member"}
    )[0]


def make_user(email, first_name="Test", last_name="User", phone="+420123456789"):
    return User.objects.create(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        _str=f"{first_name} {last_name}",
    )


def make_fundraiser(email, fundraiser_role, first_name="Fundraiser", last_name="User"):
    user = make_user(email, first_name, last_name)
    user.roles.add(fundraiser_role)
    return user


def make_donor(user):
    return Donor.objects.create(user=user)


def add_to_campaign(user, campaign, categories, created_at=None):
    event = DonorEvent.objects.create(
        user=user,
        event_type=categories["added_to_campaign"],
        campaign=campaign,
    )
    if created_at:
        DonorEvent.objects.filter(pk=event.pk).update(created_at=created_at)
    return event


def log_call(user, campaign, categories, slug, created_at=None, reminder=None):
    event = DonorEvent.objects.create(
        user=user,
        event_type=categories[slug],
        campaign=campaign,
        reminder=reminder,
    )
    if created_at:
        DonorEvent.objects.filter(pk=event.pk).update(created_at=created_at)
    return event


@pytest.mark.django_db
def test_worklist_excludes_donors_with_4_calls(categories, campaign):
    person = make_user("donor4@example.com")
    add_to_campaign(person, campaign, categories)

    now = timezone.now()
    for _ in range(4):
        log_call(person, campaign, categories, "call_no_answer", created_at=now)

    assert person not in list(get_worklist(campaign))


@pytest.mark.django_db
def test_worklist_includes_donor_with_3_calls(categories, campaign):
    person = make_user("donor3@example.com")
    add_to_campaign(person, campaign, categories)

    now = timezone.now()
    for _ in range(3):
        log_call(person, campaign, categories, "call_no_answer", created_at=now)

    assert person in list(get_worklist(campaign))


@pytest.mark.django_db
def test_postponed_reminder_resets_window(categories, campaign):
    person = make_user("donor_postponed@example.com")

    base_time = timezone.now() - timedelta(days=10)
    add_to_campaign(person, campaign, categories, created_at=base_time)

    for i in range(4):
        log_call(
            person,
            campaign,
            categories,
            "call_no_answer",
            created_at=base_time + timedelta(hours=i + 1),
        )

    now = timezone.now()
    assert person not in list(get_worklist(campaign))

    # Log postponement after the 4 old calls — window resets
    reminder_event_time = base_time + timedelta(days=5)
    reminder_due = now - timedelta(hours=1)
    log_call(
        person,
        campaign,
        categories,
        "call_postponed",
        created_at=reminder_event_time,
        reminder=reminder_due,
    )

    reminders = list(get_reminders_due(campaign))
    assert person in reminders

    # Making a call after the postponement moves person out of reminders into worklist
    log_call(person, campaign, categories, "call_no_answer", created_at=now)
    assert person not in list(get_reminders_due(campaign))
    assert person in list(get_worklist(campaign))


@pytest.mark.django_db
def test_reminders_due_surfaces_overdue_reminders(categories, campaign):
    person = make_user("donor_reminder@example.com")

    past = timezone.now() - timedelta(days=5)
    add_to_campaign(person, campaign, categories, created_at=past)
    reminder_due = timezone.now() - timedelta(hours=1)
    log_call(
        person,
        campaign,
        categories,
        "call_postponed",
        created_at=past + timedelta(hours=1),
        reminder=reminder_due,
    )

    assert person in list(get_reminders_due(campaign))


@pytest.mark.django_db
def test_future_reminder_appears_in_reminders_not_worklist(categories, campaign):
    person = make_user("donor_future_reminder@example.com")

    past = timezone.now() - timedelta(days=2)
    add_to_campaign(person, campaign, categories, created_at=past)
    future_reminder = timezone.now() + timedelta(days=1)
    log_call(
        person,
        campaign,
        categories,
        "call_postponed",
        created_at=past + timedelta(hours=1),
        reminder=future_reminder,
    )

    assert person in list(get_reminders_due(campaign))
    assert person not in list(get_worklist(campaign))


@pytest.mark.django_db
def test_donor_with_reminder_goes_to_reminders_not_worklist(categories, campaign):
    person = make_user("donor_reminder2@example.com")

    past = timezone.now() - timedelta(days=2)
    add_to_campaign(person, campaign, categories, created_at=past)
    future_reminder = timezone.now() + timedelta(days=1)
    log_call(
        person,
        campaign,
        categories,
        "call_postponed",
        created_at=timezone.now() - timedelta(minutes=30),
        reminder=future_reminder,
    )

    assert person in list(get_reminders_due(campaign))
    assert person not in list(get_worklist(campaign))


@pytest.mark.django_db
def test_call_form_accepts_postponed_without_reminder(
    categories, campaign, fundraiser_role
):
    caller = make_fundraiser("fr1@example.com", fundraiser_role)
    person = make_user("donor_form@example.com")
    add_to_campaign(person, campaign, categories)

    client = Client()
    client.force_login(caller)

    url = reverse("admin:donations_telesales_call", args=[campaign.id, person.id])
    response = client.post(
        url,
        {"outcome": "call_postponed", "fundraisers_note": "", "pledge": ""},
    )

    assert response.status_code == 302
    assert DonorEvent.objects.filter(
        user=person, event_type__slug="call_postponed"
    ).exists()


@pytest.mark.django_db
def test_call_page_works_for_someone_without_donor_profile(
    categories, campaign, fundraiser_role
):
    caller = make_fundraiser("fr4@example.com", fundraiser_role)
    prospect = make_user("prospect_call@example.com", first_name="Prospekt")
    add_to_campaign(prospect, campaign, categories)

    client = Client()
    client.force_login(caller)

    url = reverse("admin:donations_telesales_call", args=[campaign.id, prospect.id])
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Prospekt" in content
    assert "Profil dárce" not in content


@pytest.mark.django_db
def test_user_page_shows_the_campaign_history(categories, campaign, fundraiser_role):
    caller = make_fundraiser("fr5@example.com", fundraiser_role)
    prospect = make_user("prospect_history@example.com")
    add_to_campaign(prospect, campaign, categories)

    client = Client()
    client.force_login(caller)

    response = client.get(reverse("admin:bis_user_change", args=[prospect.id]))

    assert response.status_code == 200
    assert "campaign_events-group" in response.content.decode()


@pytest.mark.django_db
def test_call_form_stores_contact_preferences_on_the_user(
    categories, campaign, fundraiser_role
):
    caller = make_fundraiser("fr3@example.com", fundraiser_role)
    person = make_user("donor_form3@example.com")
    add_to_campaign(person, campaign, categories)

    client = Client()
    client.force_login(caller)

    url = reverse("admin:donations_telesales_call", args=[campaign.id, person.id])
    client.post(
        url,
        {
            "outcome": "call_reached",
            "fundraisers_note": "",
            "pledge": "",
            "do_not_call": "on",
        },
    )

    person.refresh_from_db()
    assert person.do_not_call
    assert not person.do_not_solicit


@pytest.mark.django_db
def test_call_form_rejects_postponed_with_past_reminder(
    categories, campaign, fundraiser_role
):
    caller = make_fundraiser("fr2@example.com", fundraiser_role)
    person = make_user("donor_form2@example.com")

    client = Client()
    client.force_login(caller)

    past = (timezone.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
    url = reverse("admin:donations_telesales_call", args=[campaign.id, person.id])
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

    url_call = reverse(
        "admin:donations_telesales_call", args=[campaign.id, non_fundraiser.pk]
    )
    response_call = client.get(url_call)
    assert response_call.status_code == 403

    response_admin = client.get(
        reverse("admin:donations_fundraisingcampaign_changelist")
    )
    assert response_admin.status_code == 403


@pytest.mark.django_db
def test_fundraiser_can_see_donors_in_worklist(categories, campaign):
    person = make_user("donor_vis@example.com")
    add_to_campaign(person, campaign, categories)

    assert person in list(get_worklist(campaign))


@pytest.mark.django_db
def test_donor_without_phone_goes_to_finished(categories, campaign):
    person = make_user("donor_nophone@example.com", phone="")
    add_to_campaign(person, campaign, categories)

    assert person not in list(get_worklist(campaign))
    assert person not in list(get_reminders_due(campaign))
    assert person in list(get_finished(campaign))


@pytest.mark.django_db
def test_do_not_call_donor_goes_to_finished(categories, campaign):
    person = make_user("donor_dnc@example.com")
    person.do_not_call = True
    person.save()
    add_to_campaign(person, campaign, categories)

    assert person not in list(get_worklist(campaign))
    assert person not in list(get_reminders_due(campaign))
    assert person in list(get_finished(campaign))


@pytest.mark.django_db
def test_do_not_solicit_donor_goes_to_finished(categories, campaign):
    person = make_user("donor_dns@example.com")
    person.do_not_solicit = True
    person.save()
    add_to_campaign(person, campaign, categories)

    assert person not in list(get_worklist(campaign))
    assert person not in list(get_reminders_due(campaign))
    assert person in list(get_finished(campaign))


def post_campaign_action(client, url, target_ids, operation, campaign):
    return client.post(
        url,
        {
            "action": "change_fundraising_campaign",
            helpers.ACTION_CHECKBOX_NAME: [str(pk) for pk in target_ids],
            "apply": "1",
            "operation": operation,
            "campaign": campaign.pk,
        },
    )


@pytest.mark.django_db
def test_user_action_adds_users_to_campaign_without_donor_profiles(
    categories, campaign, fundraiser_role
):
    caller = make_fundraiser("fr_action@example.com", fundraiser_role)
    prospect = make_user("prospect@example.com")
    donor = make_donor(make_user("existing_donor@example.com"))

    client = Client()
    client.force_login(caller)
    url = reverse("admin:bis_user_changelist")

    post_campaign_action(
        client, url, [prospect.pk, donor.user.pk], "added_to_campaign", campaign
    )

    assert set(get_worklist(campaign)) == {prospect, donor.user}
    assert not Donor.objects.filter(user=prospect).exists()

    post_campaign_action(client, url, [prospect.pk], "remove", campaign)

    assert list(get_worklist(campaign)) == [donor.user]


@pytest.mark.django_db
def test_user_action_hidden_without_donor_add_permission(
    categories, campaign, education_member_role
):
    caller = make_user("education@example.com")
    caller.roles.add(education_member_role)
    prospect = make_user("prospect2@example.com")

    client = Client()
    client.force_login(caller)

    post_campaign_action(
        client,
        reverse("admin:bis_user_changelist"),
        [prospect.pk],
        "added_to_campaign",
        campaign,
    )

    assert not DonorEvent.objects.filter(user=prospect).exists()


@pytest.mark.django_db
def test_donor_tag_needs_a_gift_unless_legacy():
    prospect = make_donor(make_user("tag_prospect@example.com"))
    legacy = make_donor(make_user("tag_legacy@example.com"))
    legacy.date_joined = GIFTLESS_DONOR_CUTOFF - timedelta(days=1)
    legacy.save()
    giver = make_donor(make_user("tag_giver@example.com"))
    Donation.objects.create(
        donor=giver,
        donated_at=timezone.now().date(),
        amount=100,
        donation_source=DonationSourceCategory.objects.create(slug="test", name="Test"),
    )

    assert "Dárce" not in compute_tags(prospect.user)
    assert "Dárce" in compute_tags(legacy.user)
    assert "Dárce" in compute_tags(giver.user)
