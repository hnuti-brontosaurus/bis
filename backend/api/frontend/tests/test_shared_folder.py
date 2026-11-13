import pytest
from api.frontend import views
from django.test import Client


@pytest.mark.django_db
def test_event_exposes_the_shared_folder_link(api_client, event):
    response = api_client.get(f"/api/frontend/events/{event.id}/")

    assert response.data["shared_folder_link"].endswith(
        f"/api/frontend/events/{event.uid}/shared_folder/"
    )


@pytest.mark.django_db
def test_link_redirects_to_an_existing_folder(event):
    event.shared_folder_url = "https://drive.google.com/drive/folders/abc"
    event.save(update_fields=["shared_folder_url"])

    response = Client().get(f"/api/frontend/events/{event.uid}/shared_folder/")

    assert response.status_code == 302
    assert response.url == event.shared_folder_url


@pytest.mark.django_db
def test_link_shows_a_waiting_page_without_creating_the_folder(event, monkeypatch):
    monkeypatch.setattr(views, "get_or_create_shared_folder_url", pytest.fail)

    response = Client().get(f"/api/frontend/events/{event.uid}/shared_folder/")

    assert response.status_code == 200
    assert b'fetch("create/"' in response.content


@pytest.mark.django_db
def test_create_returns_the_folder_url(event, monkeypatch):
    monkeypatch.setattr(
        views, "get_or_create_shared_folder_url", lambda event: "https://drive/x"
    )

    response = Client().post(f"/api/frontend/events/{event.uid}/shared_folder/create/")

    assert response.json() == {"url": "https://drive/x"}
