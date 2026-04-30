import io

import pytest
from bis.models import User
from cookbook.models.chefs import Chef
from cookbook.models.ingredients import Ingredient
from cookbook.models.recipes import Recipe, RecipeIngredient, RecipeStep, RecipeTip
from cookbook_categories.models import (
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


def _png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _disable_groq(settings):
    """The Ingredient pre_save signal calls Groq if GROQ_API_KEY is set.
    Disable for the test session so tests don't hit the network.
    """
    settings.GROQ_API_KEY = ""


@pytest.fixture
def image_file():
    return SimpleUploadedFile("test.png", _png_bytes(), content_type="image/png")


@pytest.fixture
def chef_user(db):
    user = User.objects.create(
        first_name="Chef",
        last_name="Tester",
        email="chef-tester@example.com",
    )
    Token.objects.get_or_create(user=user)
    return user


@pytest.fixture
def chef(chef_user):
    return Chef.objects.create(
        user=chef_user,
        name="Chef Tester",
        email="chef-tester@example.com",
    )


@pytest.fixture
def difficulty(db):
    return RecipeDifficulty.objects.create(name="snadná", slug="easy", order=1)


@pytest.fixture
def required_time(db):
    return RecipeRequiredTime.objects.create(name="rychlé", slug="fast", order=1)


@pytest.fixture
def tag(db):
    return RecipeTag.objects.create(
        name="dezert", slug="dessert", order=1, group="Chody"
    )


@pytest.fixture
def unit(db):
    return Unit.objects.create(
        name="lžíce",
        slug="spoon",
        order=1,
        name2="lžíce",
        name5="lžic",
        abbreviation="lž",
        of="volume",
    )


@pytest.fixture
def ingredient(db):
    return Ingredient.objects.create(name="cukr")


@pytest.fixture
def recipe(chef, difficulty, required_time, tag, unit, ingredient, image_file):
    r = Recipe.objects.create(
        name="Test recipe",
        chef=chef,
        difficulty=difficulty,
        required_time=required_time,
        photo=image_file,
        intro="An intro",
        sources="Some sources",
    )
    r.tags.add(tag)
    RecipeIngredient.objects.create(
        recipe=r, order=0, ingredient=ingredient, unit=unit, amount=1.0
    )
    RecipeStep.objects.create(recipe=r, order=0, name="Step one", description="Do it")
    RecipeTip.objects.create(recipe=r, name="Tip", description="Be careful")
    return r


@pytest.fixture
def api_client(chef_user):
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=chef_user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client
