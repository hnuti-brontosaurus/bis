from datetime import date, timedelta

import pytest
from bis.models import User
from categories.models import RoleCategory
from django.contrib.admin import helpers
from django.test import Client
from django.urls import reverse
from donations.models import Donor
from other.models import UserTag


@pytest.fixture
def office_worker_role(db):
    return RoleCategory.objects.get_or_create(
        slug="office_worker", defaults={"name": "Office worker"}
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


def make_office_worker(email, role):
    user = make_user(email, "Office", "Worker")
    user.roles.add(role)
    return user


def post_tag_action(client, url, target_ids, operation, name):
    return client.post(
        url,
        {
            "action": "change_user_tag",
            helpers.ACTION_CHECKBOX_NAME: [str(pk) for pk in target_ids],
            "apply": "1",
            "operation": operation,
            "name": name,
        },
    )


@pytest.mark.django_db
def test_add_creates_tag_with_default_ttl(office_worker_role):
    actor = make_office_worker("actor@example.com", office_worker_role)
    target = make_user("target@example.com")

    client = Client()
    client.force_login(actor)

    url = reverse("admin:bis_user_changelist")
    response = post_tag_action(client, url, [target.pk], "add", "newsletter-2026")

    assert response.status_code == 302
    tag = UserTag.objects.get(name="newsletter-2026")
    assert list(tag.users.all()) == [target]
    expected = date.today() + timedelta(days=7)
    assert tag.expires_at == expected


@pytest.mark.django_db
def test_add_reuses_existing_tag(office_worker_role):
    actor = make_office_worker("actor3@example.com", office_worker_role)
    target_a = make_user("a@example.com")
    target_b = make_user("b@example.com")

    existing = UserTag.objects.create(
        name="reuse-me",
        expires_at=date.today() + timedelta(days=2),
    )
    existing.users.add(target_a)
    original_expiry = existing.expires_at

    client = Client()
    client.force_login(actor)

    post_tag_action(
        client,
        reverse("admin:bis_user_changelist"),
        [target_b.pk],
        "add",
        "reuse-me",
    )

    existing.refresh_from_db()
    assert set(existing.users.all()) == {target_a, target_b}
    assert existing.expires_at == original_expiry  # unchanged for existing tag


@pytest.mark.django_db
def test_remove_action(office_worker_role):
    actor = make_office_worker("actor4@example.com", office_worker_role)
    target = make_user("target4@example.com")
    tag = UserTag.objects.create(
        name="drop", expires_at=date.today() + timedelta(days=1)
    )
    tag.users.add(target)

    client = Client()
    client.force_login(actor)

    post_tag_action(
        client,
        reverse("admin:bis_user_changelist"),
        [target.pk],
        "remove",
        "drop",
    )

    tag.refresh_from_db()
    assert list(tag.users.all()) == []


@pytest.mark.django_db
def test_remove_nonexistent_tag_errors(office_worker_role):
    actor = make_office_worker("actor5@example.com", office_worker_role)
    target = make_user("target5@example.com")

    client = Client()
    client.force_login(actor)

    response = post_tag_action(
        client,
        reverse("admin:bis_user_changelist"),
        [target.pk],
        "remove",
        "does-not-exist",
    )

    assert response.status_code == 302
    assert not UserTag.objects.filter(name="does-not-exist").exists()


@pytest.mark.django_db
def test_donor_admin_tags_underlying_user(office_worker_role):
    actor = make_office_worker("actor6@example.com", office_worker_role)
    donor_user = make_user("donor_user@example.com")
    donor = Donor.objects.create(user=donor_user)

    client = Client()
    client.force_login(actor)

    response = post_tag_action(
        client,
        reverse("admin:donations_donor_changelist"),
        [donor.pk],
        "add",
        "via-donor",
    )

    assert response.status_code == 302
    tag = UserTag.objects.get(name="via-donor")
    assert list(tag.users.all()) == [donor_user]


@pytest.mark.django_db
def test_action_hidden_for_non_office_worker(board_member_role):
    actor = make_user("board@example.com")
    actor.roles.add(board_member_role)

    client = Client()
    client.force_login(actor)

    response = client.get(reverse("admin:bis_user_changelist"))
    assert b"change_user_tag" not in response.content


@pytest.mark.django_db
def test_filter_hidden_for_non_office_worker(board_member_role):
    actor = make_user("board2@example.com")
    actor.roles.add(board_member_role)

    tagged = make_user("tagged@example.com")
    tag = UserTag.objects.create(
        name="secret-cohort", expires_at=date.today() + timedelta(days=1)
    )
    tag.users.add(tagged)

    client = Client()
    client.force_login(actor)

    response = client.get(reverse("admin:bis_user_changelist"))
    assert b"secret-cohort" not in response.content


@pytest.mark.django_db
def test_filter_visible_for_office_worker(office_worker_role):
    actor = make_office_worker("actor7@example.com", office_worker_role)
    tagged = make_user("tagged-visible@example.com")
    tag = UserTag.objects.create(
        name="visible-tag", expires_at=date.today() + timedelta(days=1)
    )
    tag.users.add(tagged)

    client = Client()
    client.force_login(actor)

    response = client.get(
        reverse("admin:bis_user_changelist") + f"?tags__id__in={tag.pk}"
    )
    assert response.status_code == 200
    assert tagged.email.encode() in response.content


@pytest.mark.django_db
def test_user_tag_admin_blocked_for_non_office_worker(board_member_role):
    actor = make_user("board3@example.com")
    actor.roles.add(board_member_role)

    client = Client()
    client.force_login(actor)

    response = client.get(reverse("admin:other_usertag_changelist"))
    assert response.status_code in (302, 403)


@pytest.mark.django_db
def test_user_tag_admin_visible_for_office_worker(office_worker_role):
    actor = make_office_worker("actor8@example.com", office_worker_role)

    client = Client()
    client.force_login(actor)

    response = client.get(reverse("admin:other_usertag_changelist"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_nightly_purges_expired_tags(office_worker_role):
    expired = UserTag.objects.create(
        name="expired", expires_at=date.today() - timedelta(days=1)
    )
    fresh = UserTag.objects.create(
        name="fresh", expires_at=date.today() + timedelta(days=1)
    )

    UserTag.remove_expired()

    assert not UserTag.objects.filter(pk=expired.pk).exists()
    assert UserTag.objects.filter(pk=fresh.pk).exists()


@pytest.mark.django_db
def test_compute_tags_includes_user_tag():
    from ecomail.tags import compute_tags

    user = make_user("compute@example.com")
    UserTag.objects.create(
        name="my-tag", expires_at=date.today() + timedelta(days=1)
    ).users.add(user)

    tags = compute_tags(user)
    assert "my-tag" in tags
