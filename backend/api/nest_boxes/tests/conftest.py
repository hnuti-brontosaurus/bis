import pytest
from bis.models import User
from django.core.cache import cache

# The domain tests' fixtures: area, batch, make_box, manager, movement, unit…
from nest_boxes.tests.conftest import *  # noqa: F403
from rest_framework.test import APIClient

API = "/api/nest_boxes"


@pytest.fixture(autouse=True)
def no_throttle_history():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def client_for():
    def make(user=None):
        client = APIClient()
        if user is not None:
            client.force_authenticate(User.objects.get(pk=user.pk))
        return client

    return make


@pytest.fixture
def anonymous(client_for):
    return client_for()


@pytest.fixture
def board_member(movement, unit, manager):
    unit.board_members.add(manager)
    return manager


@pytest.fixture
def board_client(client_for, board_member):
    return client_for(board_member)


@pytest.fixture
def budkar(movement):
    user = User.objects.create(email="budkar@example.com")
    movement.nest_box_managers.add(user)
    return user


@pytest.fixture
def stranger(movement):
    return User.objects.create(email="stranger@example.com")
