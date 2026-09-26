"""Writable-shape tests for donor flags in the frontend user API.

Donor.do_not_call / do_not_solicit are exposed through DonorSerializer and
must be writable via the nested `donor` object of PATCH /api/frontend/users/,
but only when the request edits the requesting user themself (the donor
sub-object is excluded from every payload about anybody else).
"""

import pytest
from bis.models import User
from donations.models import Donor
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.fixture
def api_client(user):
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def user(db):
    return User.objects.create(
        first_name="Don",
        last_name="Or",
        email="donor-flags@example.com",
    )


@pytest.fixture
def donor(user):
    return Donor.objects.create(user=user)


@pytest.mark.django_db
def test_donor_flags_present_on_read(api_client, user, donor):
    response = api_client.get(f"/api/frontend/users/{user.id}/", format="json")
    assert response.status_code == 200, response.data
    assert response.data["donor"]["do_not_call"] is False
    assert response.data["donor"]["do_not_solicit"] is False


@pytest.mark.django_db
def test_donor_flags_writable_on_patch(api_client, user, donor):
    response = api_client.patch(
        f"/api/frontend/users/{user.id}/",
        {"donor": {"do_not_call": True, "do_not_solicit": True}},
        format="json",
    )
    assert response.status_code == 200, response.data
    donor.refresh_from_db()
    assert donor.do_not_call is True
    assert donor.do_not_solicit is True
    assert response.data["donor"]["do_not_call"] is True
    assert response.data["donor"]["do_not_solicit"] is True


@pytest.mark.django_db
def test_donor_flags_round_trip_toggle_back(api_client, user, donor):
    set_response = api_client.patch(
        f"/api/frontend/users/{user.id}/",
        {"donor": {"do_not_call": True}},
        format="json",
    )
    assert set_response.status_code == 200, set_response.data
    unset_response = api_client.patch(
        f"/api/frontend/users/{user.id}/",
        {"donor": {"do_not_call": False}},
        format="json",
    )
    assert unset_response.status_code == 200, unset_response.data
    donor.refresh_from_db()
    assert donor.do_not_call is False


@pytest.mark.django_db
def test_donor_hidden_for_other_user(api_client, user, db):
    # a fundraiser can view anybody, but donor is only shown for themself
    from categories.models import RoleCategory

    fundraiser_role = RoleCategory.objects.get_or_create(
        slug="fundraiser", defaults={"name": "Fundraiser"}
    )[0]
    user.roles.add(fundraiser_role)

    other = User.objects.create(
        first_name="Oth",
        last_name="Er",
        email="donor-flags-other@example.com",
    )
    response = api_client.get(f"/api/frontend/users/{other.id}/", format="json")
    assert response.status_code == 200, response.data
    assert "donor" not in response.data

    own_response = api_client.get(f"/api/frontend/users/{user.id}/", format="json")
    assert own_response.status_code == 200, own_response.data
    assert "donor" in own_response.data
