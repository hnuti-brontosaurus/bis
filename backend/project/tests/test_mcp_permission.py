import pytest
from bis.models import User
from django.test import RequestFactory


def make_user(email):
    return User.objects.create(
        email=email,
        first_name="Test",
        last_name="User",
        _str="Test User",
    )


@pytest.fixture
def mcp_permission(db):
    # project.urls pulls in api.urls, whose filters query the DB at import
    # time, so it must only be imported once the db fixture is active.
    from project.urls import MCPPermission

    return MCPPermission()


@pytest.fixture
def request_with_user(db, django_user_model):
    def _make(user):
        request = RequestFactory().get("/mcp")
        request.user = user
        return request

    return _make


@pytest.mark.django_db
def test_anonymous_user_denied(request_with_user, mcp_permission):
    class AnonymousUser:
        is_staff = False
        email = None

    request = request_with_user(AnonymousUser())
    assert not mcp_permission.has_permission(request, None)


@pytest.mark.django_db
def test_non_staff_user_denied(request_with_user, mcp_permission):
    request = request_with_user(make_user("member@example.com"))
    assert not mcp_permission.has_permission(request, None)


@pytest.mark.django_db
def test_brontobot_allowed_without_staff(request_with_user, mcp_permission):
    request = request_with_user(make_user("brontosaurus.bot@gmail.com"))
    assert mcp_permission.has_permission(request, None)


@pytest.mark.django_db
def test_staff_user_allowed(request_with_user, mcp_permission):
    from bis.models import RoleCategory

    role = RoleCategory.objects.get_or_create(
        slug="board_member", defaults={"name": "Board member"}
    )[0]
    user = make_user("staff@example.com")
    user.roles.add(role)
    request = request_with_user(user)
    assert mcp_permission.has_permission(request, None)
