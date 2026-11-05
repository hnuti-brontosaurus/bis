import pytest
from cookbook_categories.models import RecipeTag

URL = "/api/cookbook/recipe_tags/"


@pytest.mark.django_db
def test_editor_adds_tag_to_the_end_of_a_group(editor_client, tag):
    response = editor_client.post(URL, {"name": "Koláč", "group": tag.group})
    assert response.status_code == 201, response.data
    created = RecipeTag.objects.get(id=response.data["id"])
    assert (created.slug, created.order) == ("kolac", tag.order + 1)


@pytest.mark.django_db
def test_new_tag_is_listed_at_once(editor_client, tag):
    editor_client.get(URL)
    editor_client.post(URL, {"name": "Koláč", "group": tag.group})
    names = {row["name"] for row in editor_client.get(URL).data["results"]}
    assert "Koláč" in names


@pytest.mark.django_db
def test_tag_slug_stays_unique(editor_client, tag):
    RecipeTag.objects.create(name="X", slug="kolac", order=5, group="Jiné")
    response = editor_client.post(URL, {"name": "Koláč", "group": tag.group})
    assert response.data["slug"] == "kolac-2"


@pytest.mark.django_db
def test_tag_name_is_unique_within_its_group(editor_client, tag):
    response = editor_client.post(URL, {"name": tag.name.upper(), "group": tag.group})
    assert response.status_code == 400
    assert "name" in response.data


@pytest.mark.django_db
def test_tag_group_must_exist(editor_client, tag):
    response = editor_client.post(URL, {"name": "Nový", "group": "Nová skupina"})
    assert response.status_code == 400
    assert "group" in response.data


@pytest.mark.django_db
def test_only_editors_add_tags(api_client, anon_client, tag):
    for client in (api_client, anon_client):
        response = client.post(URL, {"name": "Koláč", "group": tag.group})
        assert response.status_code in (401, 403)
    assert not RecipeTag.objects.filter(name="Koláč").exists()
