from bis.models import User
from django.contrib.auth.models import AnonymousUser
from nest_boxes.permissions import is_manager


def fresh(user):
    return User.objects.get(pk=user.pk)


def test_budkar_manages(movement, manager):
    movement.nest_box_managers.add(manager)
    assert is_manager(fresh(manager))


def test_board_member_does_not_manage(movement, unit, manager):
    unit.board_members.add(manager)
    assert not is_manager(fresh(manager))


def test_others_do_not_manage(movement, manager):
    assert not is_manager(manager)
    assert not is_manager(AnonymousUser())


def test_superuser_manages(movement):
    assert is_manager(fresh(movement.director))
