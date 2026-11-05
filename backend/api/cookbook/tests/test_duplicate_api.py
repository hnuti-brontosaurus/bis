import pytest
from cookbook.models.recipes import (
    Recipe,
    RecipeIngredientPhoto,
    RecipeStepPhoto,
    RecipeTipPhoto,
)


def _url(recipe):
    return f"/api/cookbook/recipes/{recipe.id}/duplicate/"


@pytest.fixture
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)


@pytest.fixture
def recipe_with_photos(media_root, recipe, image_file):
    recipe.is_public = True
    recipe.save()
    for model, parent in (
        (RecipeIngredientPhoto, recipe.ingredients.get()),
        (RecipeStepPhoto, recipe.steps.get()),
        (RecipeTipPhoto, recipe.tips.get()),
    ):
        image_file.seek(0)
        model.objects.create(parent=parent, order=0, photo=image_file)
    return recipe


@pytest.mark.django_db
def test_other_chef_duplicates_into_a_private_copy(
    other_client, other_chef, recipe_with_photos
):
    recipe = recipe_with_photos
    response = other_client.post(_url(recipe))
    assert response.status_code == 201, response.data

    copy = Recipe.objects.get(id=response.data["id"])
    assert response.data["original_id"] == recipe.id
    assert copy.chef == other_chef
    assert copy.name == "Test recipe - kopie"
    assert not copy.is_public
    assert copy.sources == (
        f'Some sources<p>Původní recept: <a href="/kucharka/recept/{recipe.id}/">'
        "Test recipe</a></p>"
    )
    assert set(copy.tags.all()) == set(recipe.tags.all())
    assert copy.ingredients.get().ingredient == recipe.ingredients.get().ingredient
    assert copy.steps.get().name == "Step one"
    assert copy.tips.get().name == "Tip"

    originals = [recipe.photos.get(), recipe.ingredients.get().photos.get()]
    copies = [copy.photos.get(), copy.ingredients.get().photos.get()]
    copies += [copy.steps.get().photos.get(), copy.tips.get().photos.get()]
    assert len(copies) == 4
    for original, duplicate in zip(originals, copies):
        assert duplicate.photo.name != original.photo.name

    # The copy owns its files, so deleting it leaves the original's intact.
    copy.delete()
    for photo in originals:
        photo.photo.open()
        photo.photo.close()


@pytest.mark.django_db
def test_copy_name_fits_the_name_limit(media_root, api_client, recipe):
    recipe.name = "x" * 31
    recipe.save()
    response = api_client.post(_url(recipe))
    assert response.status_code == 201, response.data
    assert response.data["name"] == "x" * 23 + " - kopie"


@pytest.mark.django_db
def test_duplicate_needs_a_chef_who_can_read_the_recipe(
    other_client, non_chef_client, anon_client, recipe
):
    assert other_client.post(_url(recipe)).status_code == 404
    recipe.is_public = True
    recipe.save()
    assert non_chef_client.post(_url(recipe)).status_code == 403
    assert anon_client.post(_url(recipe)).status_code == 401
    assert Recipe.objects.count() == 1
