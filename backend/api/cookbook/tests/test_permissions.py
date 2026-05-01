"""Permission tests for the cookbook API.

Exercises the rules in `api/cookbook/permissions.py`:

- Recipe / Menu visibility (editor / chef / anonymous)
- Recipe / Menu writes restricted to owner or editor
- Ingredient writes restricted to chefs; deletion blocked when in use
- Chef writes restricted to self; deletion forbidden
"""

import pytest
from bis.models import User
from cookbook.models.chefs import Chef
from cookbook.models.menus import Menu
from cookbook.models.recipes import Recipe
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

# ---------- helpers ----------


def _make_chef_user(email, name="Other"):
    user = User.objects.create(first_name=name, last_name="X", email=email)
    Token.objects.get_or_create(user=user)
    return user


def _make_chef(user, is_editor=False):
    return Chef.objects.create(
        user=user,
        name=user.first_name,
        email=user.email,
        is_editor=is_editor,
    )


def _client_for(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {user.auth_token.key}")
    return client


# ---------- fixtures ----------


@pytest.fixture
def other_chef_user(db):
    return _make_chef_user("other@example.com", name="Other")


@pytest.fixture
def other_chef(other_chef_user):
    return _make_chef(other_chef_user)


@pytest.fixture
def other_client(other_chef_user, other_chef):
    return _client_for(other_chef_user)


@pytest.fixture
def editor_user(db):
    return _make_chef_user("editor@example.com", name="Editor")


@pytest.fixture
def editor(editor_user):
    return _make_chef(editor_user, is_editor=True)


@pytest.fixture
def editor_client(editor_user, editor):
    return _client_for(editor_user)


@pytest.fixture
def non_chef_user(db):
    return _make_chef_user("plain@example.com", name="Plain")


@pytest.fixture
def non_chef_client(non_chef_user):
    return _client_for(non_chef_user)


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.fixture
def other_recipe_public(other_chef, difficulty, required_time, image_file):
    return Recipe.objects.create(
        name="Other public",
        chef=other_chef,
        difficulty=difficulty,
        required_time=required_time,
        photo=image_file,
        intro="x",
        sources="x",
        is_public=True,
    )


@pytest.fixture
def other_recipe_private(other_chef, difficulty, required_time, image_file):
    return Recipe.objects.create(
        name="Other private",
        chef=other_chef,
        difficulty=difficulty,
        required_time=required_time,
        photo=image_file,
        intro="x",
        sources="x",
        is_public=False,
    )


@pytest.fixture
def other_menu_shared(other_chef_user):
    return Menu.objects.create(name="Shared", user=other_chef_user, is_shared=True)


@pytest.fixture
def other_menu_private(other_chef_user):
    return Menu.objects.create(name="Private", user=other_chef_user, is_shared=False)


# ---------- Recipe visibility ----------


@pytest.mark.django_db
def test_recipe_list_anon_sees_only_public(
    anon_client, recipe, other_recipe_public, other_recipe_private
):
    """`recipe` fixture is owned by chef_user and is private (default)."""
    response = anon_client.get("/api/cookbook/recipes/")
    assert response.status_code == 200
    ids = {r["id"] for r in response.data["results"]}
    assert other_recipe_public.id in ids
    assert other_recipe_private.id not in ids
    assert recipe.id not in ids


@pytest.mark.django_db
def test_recipe_list_chef_sees_public_and_own(
    api_client, chef, recipe, other_recipe_public, other_recipe_private
):
    response = api_client.get("/api/cookbook/recipes/")
    assert response.status_code == 200
    ids = {r["id"] for r in response.data["results"]}
    assert recipe.id in ids  # own (private)
    assert other_recipe_public.id in ids
    assert other_recipe_private.id not in ids


@pytest.mark.django_db
def test_recipe_list_editor_sees_all(
    editor_client, recipe, other_recipe_public, other_recipe_private
):
    response = editor_client.get("/api/cookbook/recipes/")
    assert response.status_code == 200
    ids = {r["id"] for r in response.data["results"]}
    assert {recipe.id, other_recipe_public.id, other_recipe_private.id} <= ids


@pytest.mark.django_db
def test_recipe_retrieve_private_other_returns_404_for_chef(
    api_client, chef, other_recipe_private
):
    response = api_client.get(f"/api/cookbook/recipes/{other_recipe_private.id}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_recipe_retrieve_private_other_ok_for_editor(
    editor_client, other_recipe_private
):
    response = editor_client.get(f"/api/cookbook/recipes/{other_recipe_private.id}/")
    assert response.status_code == 200


# ---------- Recipe writes ----------


@pytest.mark.django_db
def test_recipe_chef_cannot_patch_other(api_client, chef, other_recipe_public):
    response = api_client.patch(
        f"/api/cookbook/recipes/{other_recipe_public.id}/",
        {"intro": "hacked"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_recipe_editor_can_patch_any(editor_client, other_recipe_private):
    response = editor_client.patch(
        f"/api/cookbook/recipes/{other_recipe_private.id}/",
        {"intro": "edited"},
        format="json",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_recipe_chef_can_delete_own(api_client, chef, recipe):
    response = api_client.delete(f"/api/cookbook/recipes/{recipe.id}/")
    assert response.status_code == 204
    assert not Recipe.objects.filter(id=recipe.id).exists()


@pytest.mark.django_db
def test_recipe_chef_cannot_delete_other(api_client, chef, other_recipe_public):
    response = api_client.delete(f"/api/cookbook/recipes/{other_recipe_public.id}/")
    assert response.status_code == 403
    assert Recipe.objects.filter(id=other_recipe_public.id).exists()


@pytest.mark.django_db
def test_recipe_editor_can_delete_any(editor_client, other_recipe_private):
    response = editor_client.delete(f"/api/cookbook/recipes/{other_recipe_private.id}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_recipe_anon_cannot_create(anon_client, chef, difficulty, required_time):
    response = anon_client.post(
        "/api/cookbook/recipes/",
        {
            "name": "x",
            "chef_id": chef.id,
            "difficulty_id": difficulty.id,
            "required_time_id": required_time.id,
            "intro": "x",
            "sources": "x",
        },
        format="json",
    )
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_recipe_chef_cannot_create_under_other_chef(
    api_client, chef, other_chef, difficulty, required_time
):
    response = api_client.post(
        "/api/cookbook/recipes/",
        {
            "name": "x",
            "chef_id": other_chef.id,
            "difficulty_id": difficulty.id,
            "required_time_id": required_time.id,
            "intro": "x",
            "sources": "x",
        },
        format="json",
    )
    assert response.status_code == 403


# ---------- Menu visibility & writes ----------


@pytest.mark.django_db
def test_menu_list_anon_sees_only_shared(
    anon_client, other_menu_shared, other_menu_private
):
    response = anon_client.get("/api/cookbook/menus/")
    ids = {m["id"] for m in response.data["results"]}
    assert other_menu_shared.id in ids
    assert other_menu_private.id not in ids


@pytest.mark.django_db
def test_menu_chef_sees_shared_plus_own(
    api_client, chef, chef_user, other_menu_shared, other_menu_private
):
    own = Menu.objects.create(name="own", user=chef_user, is_shared=False)
    response = api_client.get("/api/cookbook/menus/")
    ids = {m["id"] for m in response.data["results"]}
    assert own.id in ids
    assert other_menu_shared.id in ids
    assert other_menu_private.id not in ids


@pytest.mark.django_db
def test_menu_editor_sees_all(editor_client, other_menu_shared, other_menu_private):
    response = editor_client.get("/api/cookbook/menus/")
    ids = {m["id"] for m in response.data["results"]}
    assert {other_menu_shared.id, other_menu_private.id} <= ids


@pytest.mark.django_db
def test_menu_chef_cannot_delete_other(api_client, chef, other_menu_shared):
    response = api_client.delete(f"/api/cookbook/menus/{other_menu_shared.id}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_menu_owner_can_delete_own(api_client, chef, chef_user):
    own = Menu.objects.create(name="own", user=chef_user, is_shared=False)
    response = api_client.delete(f"/api/cookbook/menus/{own.id}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_menu_editor_can_delete_any(editor_client, other_menu_private):
    response = editor_client.delete(f"/api/cookbook/menus/{other_menu_private.id}/")
    assert response.status_code == 204


# ---------- Ingredient writes ----------


@pytest.mark.django_db
def test_ingredient_non_chef_cannot_create(non_chef_client):
    response = non_chef_client.post(
        "/api/cookbook/ingredients/", {"name": "sůl"}, format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_ingredient_chef_can_delete_unused(api_client, chef):
    from cookbook.models.ingredients import Ingredient

    ing = Ingredient.objects.create(name="paprika")
    response = api_client.delete(f"/api/cookbook/ingredients/{ing.id}/")
    assert response.status_code == 204
    assert not Ingredient.objects.filter(id=ing.id).exists()


@pytest.mark.django_db
def test_ingredient_delete_in_use_blocked_by_db(api_client, chef, recipe, ingredient):
    """Deleting an ingredient referenced by a recipe is blocked by ProtectedError."""
    from django.db.models.deletion import ProtectedError

    with pytest.raises(ProtectedError):
        api_client.delete(f"/api/cookbook/ingredients/{ingredient.id}/")


@pytest.mark.django_db
def test_ingredient_anon_cannot_create(anon_client):
    response = anon_client.post(
        "/api/cookbook/ingredients/", {"name": "sůl"}, format="json"
    )
    assert response.status_code in (401, 403)


# ---------- Chef writes ----------


@pytest.mark.django_db
def test_chef_create_self_allowed(non_chef_user, non_chef_client):
    """A logged-in user creating their own chef passes the permission gate.

    We assert non-403 rather than 201: the serializer's photo field is
    base64-only, so a bare JSON post will fail with 400 — which already
    proves permission allowed the request through.
    """
    response = non_chef_client.post(
        "/api/cookbook/chefs/",
        {"user_id": non_chef_user.id, "name": "Me", "email": non_chef_user.email},
        format="json",
    )
    assert response.status_code != 403, response.data


@pytest.mark.django_db
def test_chef_create_for_other_user_forbidden(non_chef_client, chef_user):
    response = non_chef_client.post(
        "/api/cookbook/chefs/",
        {"user_id": chef_user.id, "name": "Sneaky", "email": "x@y.z"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_chef_delete_forbidden_even_for_self(api_client, chef):
    response = api_client.delete(f"/api/cookbook/chefs/{chef.id}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_chef_delete_forbidden_for_editor(editor_client, other_chef):
    response = editor_client.delete(f"/api/cookbook/chefs/{other_chef.id}/")
    assert response.status_code == 403


# ---------- Chef visibility ----------


@pytest.mark.django_db
def test_chef_list_anon_sees_only_chefs_with_public_recipes(
    anon_client, chef, other_chef, other_recipe_public
):
    """`chef` has no public recipe; `other_chef` does."""
    response = anon_client.get("/api/cookbook/chefs/")
    ids = {c["id"] for c in response.data["results"]}
    assert other_chef.id in ids
    assert chef.id not in ids


@pytest.mark.django_db
def test_chef_list_chef_sees_publishing_authors_plus_self(
    api_client, chef, other_chef, other_recipe_public
):
    """A chef with no public recipes still sees their own chef row."""
    response = api_client.get("/api/cookbook/chefs/")
    ids = {c["id"] for c in response.data["results"]}
    assert chef.id in ids  # own
    assert other_chef.id in ids  # has public recipe


@pytest.mark.django_db
def test_chef_list_hides_silent_other(api_client, chef, other_chef):
    """A chef with no public recipes is hidden from peers."""
    response = api_client.get("/api/cookbook/chefs/")
    ids = {c["id"] for c in response.data["results"]}
    assert chef.id in ids
    assert other_chef.id not in ids


@pytest.mark.django_db
def test_chef_list_editor_sees_all(editor_client, chef, other_chef):
    response = editor_client.get("/api/cookbook/chefs/")
    ids = {c["id"] for c in response.data["results"]}
    assert {chef.id, other_chef.id} <= ids


@pytest.mark.django_db
def test_chef_retrieve_silent_other_404_for_anon(anon_client, other_chef):
    response = anon_client.get(f"/api/cookbook/chefs/{other_chef.id}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_chef_retrieve_publishing_other_ok_for_anon(
    anon_client, other_chef, other_recipe_public
):
    response = anon_client.get(f"/api/cookbook/chefs/{other_chef.id}/")
    assert response.status_code == 200


# ---------- Visibility for non-chef authenticated users ----------


@pytest.mark.django_db
def test_recipe_list_non_chef_sees_only_public(
    non_chef_client, recipe, other_recipe_public, other_recipe_private
):
    response = non_chef_client.get("/api/cookbook/recipes/")
    ids = {r["id"] for r in response.data["results"]}
    assert other_recipe_public.id in ids
    assert other_recipe_private.id not in ids
    assert recipe.id not in ids
