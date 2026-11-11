from bis.models import User
from django.contrib.auth.models import AnonymousUser
from nest_boxes.permissions import can_manage, is_manager, manageable_areas


def fresh(user):
    return User.objects.get(pk=user.pk)


def test_budkar_manages_every_area(movement, area, other_area, manager):
    movement.nest_box_managers.add(manager)
    manager = fresh(manager)
    assert is_manager(manager)
    assert set(manageable_areas(manager)) == {area, other_area}


def test_board_manages_the_units_areas(movement, unit, area, other_area, manager):
    unit.board_members.add(manager)
    manager = fresh(manager)
    assert is_manager(manager)
    assert can_manage(manager, area)
    assert not can_manage(manager, other_area)


def test_board_manages_before_the_first_area(movement, unit, manager):
    unit.board_members.add(manager)
    assert is_manager(fresh(manager))
    assert not manageable_areas(fresh(manager)).exists()


def test_units_budkar_manages_before_the_first_area(movement, unit, manager):
    unit.nest_box_managers.add(manager)
    assert is_manager(fresh(manager))
    assert not manageable_areas(fresh(manager)).exists()


def test_units_budkar_manages_the_units_areas(
    movement, unit, area, other_area, manager
):
    unit.nest_box_managers.add(manager)
    assert list(manageable_areas(fresh(manager))) == [area]


def test_others_do_not_manage(movement, area, manager):
    assert not is_manager(manager)
    assert not can_manage(manager, area)
    assert not is_manager(AnonymousUser())
    assert not manageable_areas(AnonymousUser()).exists()


def test_superuser_manages(movement, area):
    assert is_manager(fresh(movement.director))
    assert can_manage(fresh(movement.director), area)
