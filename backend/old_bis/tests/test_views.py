import pytest
from api.frontend.tests.conftest import event, movement, organizer  # noqa: F401
from django.urls import reverse

PAGES = [
    "welcome",
    "events",
    "web_events",
    "new_event",
    "locations",
    "administration_units",
    "sub_units",
    "dashboard_items",
    "search",
    "help",
    "members",
    "consultants",
]


@pytest.mark.parametrize("page", PAGES)
def test_anonymous_is_sent_to_old_login(client, db, page):
    response = client.get(reverse(f"old_bis:{page}"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("old_bis:login") + "?next=")


def test_login_page_is_public(client, db):
    assert client.get(reverse("old_bis:login")).status_code == 200


@pytest.mark.parametrize("page", PAGES)
def test_organizer_sees_every_page(client, event, page):  # noqa: F811
    client.force_login(event.main_organizer)

    assert client.get(reverse(f"old_bis:{page}")).status_code == 200


def test_events_lists_own_event(client, event):  # noqa: F811
    client.force_login(event.main_organizer)

    response = client.get(reverse("old_bis:events"))

    assert event.name in response.content.decode()


def test_search_finds_visible_people(client, event):  # noqa: F811
    client.force_login(event.main_organizer)

    response = client.get(reverse("old_bis:search"), {"pattern": "nizer"})

    assert "Orga" in response.content.decode()
