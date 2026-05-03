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
    assert body["chef_id"] == recipe.chef_id
    assert body["difficulty_id"] == recipe.difficulty_id
    assert body["required_time_id"] == recipe.required_time_id
    assert isinstance(body["tag_ids"], list)
    assert all(isinstance(t, int) for t in body["tag_ids"])
    assert "chef" not in body
    assert "difficulty" not in body
    assert "required_time" not in body
    assert "tags" not in body
    assert isinstance(body["ingredients"], list)
    assert isinstance(body["steps"], list)
    assert isinstance(body["tips"], list)
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
def test_recipe_create_private_without_photo_intro_sources(
    api_client, chef, difficulty, required_time
):
    """Non-public recipes can be saved as drafts without photo/intro/sources."""
    response = api_client.post(
        "/api/cookbook/recipes/",
        {
            "name": "Draft",
            "chef_id": chef.id,
            "difficulty_id": difficulty.id,
            "required_time_id": required_time.id,
            "is_public": False,
        },
        format="json",
    )
    assert response.status_code == 201, response.data
    assert response.data["is_public"] is False
    assert response.data["intro"] == ""
    assert response.data["sources"] == ""


@pytest.mark.django_db
def test_recipe_create_public_requires_photo_intro_sources(
    api_client, chef, difficulty, required_time
):
    """A public recipe without photo/intro/sources is rejected with field errors."""
    response = api_client.post(
        "/api/cookbook/recipes/",
        {
            "name": "Published",
            "chef_id": chef.id,
            "difficulty_id": difficulty.id,
            "required_time_id": required_time.id,
            "is_public": True,
        },
        format="json",
    )
    assert response.status_code == 400, response.data
    assert set(response.data.keys()) >= {"photo", "intro", "sources"}


@pytest.mark.django_db
def test_recipe_toggle_to_public_without_required_fields_fails(
    api_client, chef, difficulty, required_time
):
    """Toggling is_public on a draft recipe missing fields returns 400."""
    from cookbook.models.recipes import Recipe

    draft = Recipe.objects.create(
        name="Draft",
        chef=chef,
        difficulty=difficulty,
        required_time=required_time,
    )
    response = api_client.patch(
        f"/api/cookbook/recipes/{draft.id}/",
        {"is_public": True},
        format="json",
    )
    assert response.status_code == 400, response.data
    assert set(response.data.keys()) >= {"photo", "intro", "sources"}
    draft.refresh_from_db()
    assert draft.is_public is False


@pytest.mark.django_db
def test_recipe_full_create_then_edit(
    api_client, chef, difficulty, required_time, tag, unit, ingredient
):
    """End-to-end coverage: create with every nested part populated, then
    edit each part in a follow-up PATCH."""
    other_ingredient = ingredient.__class__.objects.create(name="mouka")
    other_tag = tag.__class__.objects.create(
        name="snídaně", slug="breakfast", order=2, group="Chody"
    )

    create_response = api_client.post(
        "/api/cookbook/recipes/",
        {
            "name": "Bábovka",
            "chef_id": chef.id,
            "difficulty_id": difficulty.id,
            "required_time_id": required_time.id,
            "tag_ids": [tag.id],
            "intro": "Domácí bábovka",
            "sources": "Babiččin recept",
            "is_public": False,
            "ingredients": [
                {
                    "order": 0,
                    "ingredient_id": ingredient.id,
                    "unit_id": unit.id,
                    "amount": 100.0,
                    "is_required": True,
                    "comment": "krystalový",
                },
                {
                    "order": 1,
                    "ingredient_id": other_ingredient.id,
                    "unit_id": unit.id,
                    "amount": 250.0,
                    "is_required": True,
                    "comment": "",
                },
            ],
            "steps": [
                {"order": 0, "name": "Smíchat", "description": "Suché s mokrými"},
                {"order": 1, "name": "Péct", "description": "180°C, 40 min"},
            ],
            "tips": [
                {"name": "Vychladit", "description": "Před krájením"},
            ],
        },
        format="json",
    )
    assert create_response.status_code == 201, create_response.data
    recipe_id = create_response.data["id"]

    edit_response = api_client.patch(
        f"/api/cookbook/recipes/{recipe_id}/",
        {
            "name": "Mramorová bábovka",
            "intro": "Mramorová verze",
            "sources": "Vlastní úprava",
            "tag_ids": [tag.id, other_tag.id],
            "ingredients": [
                {
                    "order": 0,
                    "ingredient_id": other_ingredient.id,
                    "unit_id": unit.id,
                    "amount": 300.0,
                    "is_required": True,
                    "comment": "hladká",
                },
                {
                    "order": 1,
                    "ingredient_id": ingredient.id,
                    "unit_id": unit.id,
                    "amount": 120.0,
                    "is_required": False,
                    "comment": "moučkový",
                },
            ],
            "steps": [
                {
                    "order": 0,
                    "name": "Rozdělit",
                    "description": "Polovinu obarvit kakaem",
                },
                {"order": 1, "name": "Vrstvit", "description": "Lžící do formy"},
                {"order": 2, "name": "Péct", "description": "170°C, 50 min"},
            ],
            "tips": [
                {"name": "Kakao", "description": "Holandského typu"},
                {"name": "Forma", "description": "Vymazat máslem a vysypat moukou"},
            ],
        },
        format="json",
    )
    assert edit_response.status_code == 200, edit_response.data

    response = api_client.get(f"/api/cookbook/recipes/{recipe_id}/")
    assert response.status_code == 200, response.data
    body = response.data
    assert body["name"] == "Mramorová bábovka"
    assert body["intro"] == "Mramorová verze"
    assert body["sources"] == "Vlastní úprava"
    assert set(body["tag_ids"]) == {tag.id, other_tag.id}

    ings = sorted(body["ingredients"], key=lambda i: i["order"])
    assert [i["order"] for i in ings] == [0, 1]
    assert [i["ingredient_id"] for i in ings] == [other_ingredient.id, ingredient.id]
    assert [i["amount"] for i in ings] == [300.0, 120.0]
    assert [i["is_required"] for i in ings] == [True, False]
    assert [i["comment"] for i in ings] == ["hladká", "moučkový"]

    steps = sorted(body["steps"], key=lambda s: s["order"])
    assert [s["name"] for s in steps] == ["Rozdělit", "Vrstvit", "Péct"]
    assert [s["description"] for s in steps] == [
        "Polovinu obarvit kakaem",
        "Lžící do formy",
        "170°C, 50 min",
    ]

    tip_names = sorted(t["name"] for t in body["tips"])
    assert tip_names == ["Forma", "Kakao"]


@pytest.mark.django_db
def test_chef_get_returns_user_id_string(api_client, chef):
    response = api_client.get(f"/api/cookbook/chefs/{chef.id}/")
    assert response.status_code == 200, response.data
    assert response.data["id"] == chef.id
    assert response.data["user_id"] == str(chef.user_id)
