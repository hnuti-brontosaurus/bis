"""Round-trip and write-shape tests for the cookbook recipe API.

Field shape rule: non-owned FK / M2M relations are exposed only as `_id`
on both read and write. Owned children (recipe ingredients/steps/tips)
nest fully on both sides.

Round-trip becomes trivial: GET -> data; PATCH(data) -> 200.
"""

import pytest


@pytest.mark.django_db
def test_recipe_get(api_client, recipe):
    response = api_client.get(f"/api/cookbook/recipes/{recipe.id}/")
    assert response.status_code == 200, response.data
    body = response.data
    # FK fields come back as ids only.
    assert body["chef_id"] == recipe.chef_id
    assert body["difficulty_id"] == recipe.difficulty_id
    assert body["required_time_id"] == recipe.required_time_id
    assert isinstance(body["tag_ids"], list)
    assert all(isinstance(t, int) for t in body["tag_ids"])
    assert "chef" not in body
    assert "difficulty" not in body
    assert "required_time" not in body
    assert "tags" not in body
    # Owned children come back as nested arrays of objects.
    assert isinstance(body["ingredients"], list)
    assert isinstance(body["steps"], list)
    assert isinstance(body["tips"], list)
    # Through rows also flatten FKs to _id.
    if body["ingredients"]:
        ing = body["ingredients"][0]
        assert "ingredient_id" in ing
        assert "unit_id" in ing
        assert "ingredient" not in ing
        assert "unit" not in ing


@pytest.mark.django_db
def test_recipe_patch_with_fk_id(api_client, recipe, difficulty):
    """Writing a FK should accept just the integer id."""
    new_difficulty = difficulty.__class__.objects.create(
        name="hard", slug="hard", order=2
    )
    response = api_client.patch(
        f"/api/cookbook/recipes/{recipe.id}/",
        {"difficulty_id": new_difficulty.id},
        format="json",
    )
    assert response.status_code == 200, response.data
    recipe.refresh_from_db()
    assert recipe.difficulty_id == new_difficulty.id


@pytest.mark.django_db
def test_recipe_patch_returns_read_shape(api_client, recipe, difficulty):
    """A PATCH response keeps the read shape — _id fields only."""
    new_difficulty = difficulty.__class__.objects.create(
        name="hard", slug="hard", order=2
    )
    response = api_client.patch(
        f"/api/cookbook/recipes/{recipe.id}/",
        {"difficulty_id": new_difficulty.id},
        format="json",
    )
    assert response.status_code == 200, response.data
    assert response.data["difficulty_id"] == new_difficulty.id
    assert isinstance(response.data["chef_id"], int)
    assert isinstance(response.data["required_time_id"], int)


@pytest.mark.django_db
def test_recipe_patch_simple_field(api_client, recipe):
    response = api_client.patch(
        f"/api/cookbook/recipes/{recipe.id}/",
        {"intro": "Updated intro"},
        format="json",
    )
    assert response.status_code == 200, response.data
    recipe.refresh_from_db()
    assert recipe.intro == "Updated intro"


@pytest.mark.django_db
def test_recipe_patch_tags_with_ids(api_client, recipe, tag):
    """Tags is a M2M; should accept a list of ids on write."""
    other = tag.__class__.objects.create(
        name="snídaně", slug="breakfast", order=2, group="Chody"
    )
    response = api_client.patch(
        f"/api/cookbook/recipes/{recipe.id}/",
        {"tag_ids": [tag.id, other.id]},
        format="json",
    )
    assert response.status_code == 200, response.data
    recipe.refresh_from_db()
    assert set(recipe.tags.values_list("id", flat=True)) == {tag.id, other.id}


@pytest.mark.django_db
def test_recipe_nested_ingredient_roundtrip(api_client, recipe, ingredient, unit):
    """Nested owned children (ingredients) should round-trip."""
    other = ingredient.__class__.objects.create(name="mouka")
    response = api_client.patch(
        f"/api/cookbook/recipes/{recipe.id}/",
        {
            "ingredients": [
                {
                    "order": 0,
                    "ingredient_id": ingredient.id,
                    "unit_id": unit.id,
                    "amount": 2.0,
                    "is_required": True,
                    "comment": "first",
                },
                {
                    "order": 1,
                    "ingredient_id": other.id,
                    "unit_id": unit.id,
                    "amount": 3.0,
                    "is_required": False,
                    "comment": "",
                },
            ]
        },
        format="json",
    )
    assert response.status_code == 200, response.data
    recipe.refresh_from_db()
    ings = list(recipe.ingredients.order_by("order"))
    assert len(ings) == 2
    assert ings[0].ingredient_id == ingredient.id
    assert ings[0].amount == 2.0
    assert ings[1].ingredient_id == other.id
    assert ings[1].amount == 3.0


@pytest.mark.django_db
def test_recipe_nested_steps_and_tips_roundtrip(api_client, recipe):
    response = api_client.patch(
        f"/api/cookbook/recipes/{recipe.id}/",
        {
            "steps": [
                {"order": 0, "name": "First", "description": "Do this"},
                {"order": 1, "name": "Second", "description": "Then that"},
            ],
            "tips": [
                {"name": "Tip A", "description": "Watch heat"},
                {"name": "Tip B", "description": "Use timer"},
            ],
        },
        format="json",
    )
    assert response.status_code == 200, response.data
    recipe.refresh_from_db()
    assert list(recipe.steps.order_by("order").values_list("name", flat=True)) == [
        "First",
        "Second",
    ]
    assert set(recipe.tips.values_list("name", flat=True)) == {"Tip A", "Tip B"}


@pytest.mark.django_db
def test_recipe_get_then_patch_roundtrip(api_client, recipe):
    """The full contract in one shot: GET payload -> PATCH it back -> 200."""
    response = api_client.get(f"/api/cookbook/recipes/{recipe.id}/")
    assert response.status_code == 200, response.data
    body = response.data
    # Strip the photo dict (write side wants either no key or a fresh upload).
    body.pop("photo", None)
    response = api_client.patch(
        f"/api/cookbook/recipes/{recipe.id}/", body, format="json"
    )
    assert response.status_code == 200, response.data


@pytest.mark.django_db
def test_chef_get_returns_user_id_string(api_client, chef):
    response = api_client.get(f"/api/cookbook/chefs/{chef.id}/")
    assert response.status_code == 200, response.data
    assert response.data["id"] == chef.id
    assert response.data["user_id"] == str(chef.user_id)
