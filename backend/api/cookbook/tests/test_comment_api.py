import base64

import pytest
from cookbook.models.recipes import RecipeComment, RecipeNote

from .conftest import _png_bytes

COMMENTS = "/api/cookbook/recipe_comments/"
NOTES = "/api/cookbook/recipe_notes/"


def _photo(parent_id):
    data = base64.b64encode(_png_bytes()).decode()
    return {
        "parent_id": parent_id,
        "order": 0,
        "photo": f"data:image/png;filename=x.png;base64,{data}",
    }


@pytest.fixture
def public_recipe(recipe):
    recipe.is_public = True
    recipe.save()
    return recipe


def _comment(client, recipe, is_public=True):
    response = client.post(
        COMMENTS,
        {"recipe_id": recipe.id, "comment": "<p>Dobré</p>", "is_public": is_public},
        format="json",
    )
    assert response.status_code == 201, response.data
    return response.data


def _listed(client, recipe):
    response = client.get(COMMENTS, {"recipe": recipe.id})
    assert response.status_code == 200, response.data
    return [comment["id"] for comment in response.data["results"]]


@pytest.mark.django_db
def test_any_signed_in_user_comments_on_a_visible_recipe(
    non_chef_client, non_chef_user, public_recipe
):
    created = _comment(non_chef_client, public_recipe)
    assert created["author"] == non_chef_user.first_name
    assert created["can_delete"]


@pytest.mark.django_db
def test_nobody_comments_on_a_recipe_they_cannot_see(
    non_chef_client, anon_client, recipe
):
    response = non_chef_client.post(
        COMMENTS, {"recipe_id": recipe.id, "comment": "x"}, format="json"
    )
    assert response.status_code == 400
    response = anon_client.post(
        COMMENTS, {"recipe_id": recipe.id, "comment": "x"}, format="json"
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_private_comment_reaches_only_the_recipe_author_and_editors(
    other_client, non_chef_client, api_client, editor_client, anon_client, public_recipe
):
    public = _comment(other_client, public_recipe)["id"]
    private = _comment(other_client, public_recipe, is_public=False)["id"]

    assert _listed(other_client, public_recipe) == [private, public]
    assert _listed(api_client, public_recipe) == [private, public]
    assert _listed(editor_client, public_recipe) == [private, public]
    assert _listed(non_chef_client, public_recipe) == [public]
    assert _listed(anon_client, public_recipe) == [public]


@pytest.mark.django_db
def test_comment_deletion(
    other_client, non_chef_client, api_client, editor_client, public_recipe
):
    first, second, third = (_comment(other_client, public_recipe) for _ in range(3))
    assert not non_chef_client.get(COMMENTS).data["results"][0]["can_delete"]

    assert non_chef_client.delete(f"{COMMENTS}{first['id']}/").status_code == 403
    assert other_client.delete(f"{COMMENTS}{first['id']}/").status_code == 204
    assert api_client.delete(f"{COMMENTS}{second['id']}/").status_code == 204
    assert editor_client.delete(f"{COMMENTS}{third['id']}/").status_code == 204
    assert not RecipeComment.objects.exists()


@pytest.mark.django_db
def test_only_the_writer_adds_photos_to_a_comment(
    other_client, non_chef_client, public_recipe
):
    comment = _comment(other_client, public_recipe)
    url = "/api/cookbook/recipe_comment_photos/"
    response = non_chef_client.post(url, _photo(comment["id"]), format="json")
    assert response.status_code == 403
    response = other_client.post(url, _photo(comment["id"]), format="json")
    assert response.status_code == 201, response.data
    assert len(other_client.get(COMMENTS).data["results"][0]["photos"]) == 1


@pytest.mark.django_db
def test_note_is_private_and_one_per_recipe(
    non_chef_client, other_client, public_recipe
):
    response = non_chef_client.post(
        NOTES, {"recipe_id": public_recipe.id, "note": "<p>2,5 dávky</p>"}
    )
    assert response.status_code == 201, response.data
    note_id = response.data["id"]

    response = non_chef_client.post(
        NOTES, {"recipe_id": public_recipe.id, "note": "again"}
    )
    assert response.status_code == 400

    assert other_client.get(NOTES, {"recipe": public_recipe.id}).data["results"] == []
    assert other_client.patch(f"{NOTES}{note_id}/", {"note": "x"}).status_code == 404
    assert (
        other_client.post(
            "/api/cookbook/recipe_note_photos/", _photo(note_id), format="json"
        ).status_code
        == 403
    )

    response = non_chef_client.patch(f"{NOTES}{note_id}/", {"note": "<p>3 dávky</p>"})
    assert response.status_code == 200, response.data
    assert non_chef_client.delete(f"{NOTES}{note_id}/").status_code == 204
    assert not RecipeNote.objects.exists()


@pytest.mark.django_db
def test_recipe_no_longer_lists_its_comments(api_client, recipe):
    assert "comments" not in api_client.get(f"/api/cookbook/recipes/{recipe.id}/").data
