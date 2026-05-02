"""Ingredient API tests.

Groq enrichment is invoked from the view's perform_create hook, not from a
pre_save signal. Both paths are covered:

- GROQ_API_KEY empty: enrichment is a no-op, the ingredient is created with
  signal-only normalization (capitalized name).
- GROQ_API_KEY set: the view calls Groq, parses the JSON, persists the
  enriched fields back onto the ingredient.
"""

from unittest.mock import MagicMock, patch

import pytest
from cookbook.models.ingredients import Ingredient


@pytest.mark.django_db
def test_create_ingredient_no_groq_key(api_client, chef, settings):
    """Without an API key, enrichment is skipped — only signal normalization."""
    settings.GROQ_API_KEY = ""
    response = api_client.post(
        "/api/cookbook/ingredients/",
        {"name": "  cukr  krupice  "},
        format="json",
    )
    assert response.status_code == 201, response.data
    # pre_save signal collapses whitespace and capitalizes on create.
    assert response.data["name"] == "Cukr krupice"


@pytest.mark.django_db
def test_create_ingredient_runs_groq_enrichment(api_client, chef, settings):
    """With an API key, the view dispatches to Groq and writes back fields."""
    settings.GROQ_API_KEY = "test-key"

    fake_completion = MagicMock()
    fake_completion.choices = [
        MagicMock(
            message=MagicMock(
                content=(
                    '{"state": "liquid", "g_per_liter": 1030, "g_per_piece": null,'
                    ' "g_per_serving": null, "allergens": [],'
                    ' "reasoning": "Mléko je tekutina."}'
                )
            )
        )
    ]
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_completion

    with patch(
        "cookbook.services.ingredient_enrichment.groq.Groq", return_value=fake_client
    ) as groq_ctor:
        response = api_client.post(
            "/api/cookbook/ingredients/",
            {"name": "mléko"},
            format="json",
        )

    assert response.status_code == 201, response.data
    groq_ctor.assert_called_once_with(api_key="test-key")
    fake_client.chat.completions.create.assert_called_once()

    instance = Ingredient.objects.get(id=response.data["id"])
    assert instance.state == "liquid"
    assert instance.g_per_liter == 1030
    assert instance.reasoning == "Mléko je tekutina."
    # Response shape mirrors the serializer fields.
    assert response.data["state"] == "liquid"
    assert response.data["g_per_liter"] == 1030


@pytest.mark.django_db
def test_create_ingredient_groq_attaches_allergens(api_client, chef, settings):
    """Allergen slugs returned by Groq become an M2M attachment."""
    from cookbook_categories.models import Allergen

    # Allergens are seeded into the test DB by the create_categories data
    # migration; just look them up rather than creating duplicates.
    settings.GROQ_API_KEY = "test-key"
    fake_completion = MagicMock()
    fake_completion.choices = [
        MagicMock(
            message=MagicMock(
                content=(
                    '{"state": "solid", "g_per_liter": 600, "g_per_piece": null,'
                    ' "g_per_serving": null, "allergens": ["gluten"],'
                    ' "reasoning": "Pšeničná mouka obsahuje lepek."}'
                )
            )
        )
    ]
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_completion

    with patch(
        "cookbook.services.ingredient_enrichment.groq.Groq", return_value=fake_client
    ):
        response = api_client.post(
            "/api/cookbook/ingredients/",
            {"name": "mouka"},
            format="json",
        )

    assert response.status_code == 201, response.data
    instance = Ingredient.objects.get(id=response.data["id"])
    assert list(instance.allergens.values_list("slug", flat=True)) == ["gluten"]
    assert response.data["allergen_ids"] == [Allergen.objects.get(slug="gluten").id]


@pytest.mark.django_db
def test_recipe_allergen_ids_unions_ingredient_allergens(
    api_client, recipe, ingredient, unit
):
    """Recipe.allergen_ids is a deduped union across the recipe's ingredients,
    cached via signals on the Recipe.allergens M2M."""
    from cookbook_categories.models import Allergen

    gluten = Allergen.objects.get(slug="gluten")
    nuts = Allergen.objects.get(slug="nuts")
    flour = ingredient.__class__.objects.create(name="mouka")
    flour.allergens.add(gluten)
    walnuts = ingredient.__class__.objects.create(name="vlašské ořechy")
    walnuts.allergens.add(nuts)
    ingredient.allergens.add(gluten)  # second source of gluten — must dedupe

    response = api_client.patch(
        f"/api/cookbook/recipes/{recipe.id}/",
        {
            "ingredients": [
                {
                    "order": 0,
                    "ingredient_id": ingredient.id,
                    "unit_id": unit.id,
                    "amount": 1.0,
                },
                {
                    "order": 1,
                    "ingredient_id": flour.id,
                    "unit_id": unit.id,
                    "amount": 2.0,
                },
                {
                    "order": 2,
                    "ingredient_id": walnuts.id,
                    "unit_id": unit.id,
                    "amount": 0.5,
                },
            ]
        },
        format="json",
    )
    assert response.status_code == 200, response.data
    response = api_client.get(f"/api/cookbook/recipes/{recipe.id}/")
    assert response.status_code == 200, response.data
    assert response.data["allergen_ids"] == sorted([gluten.id, nuts.id])
