from bis.models import User
from django.contrib.auth.models import AnonymousUser
from nest_boxes.models import Area
from nest_boxes.permissions import can_manage, can_manage_all, manageable_areas


def fresh(user):
    return User.objects.get(pk=user.pk)


def test_budkar_manages_every_area(movement, area, unit, manager):
    other = Area.objects.create(name="Jinde", administration_unit=unit)
    movement.nest_box_managers.add(manager)
    manager = fresh(manager)

    assert manager.is_nest_box_manager
    assert can_manage_all(manager)
    assert set(manageable_areas(manager)) == {area, other}


def test_board_member_manages_the_units_areas(movement, area, unit, manager):
    area.administration_unit.board_members.add(manager)
    manager = fresh(manager)

    assert can_manage(manager, area)
    assert not can_manage_all(manager)


def test_others_manage_nothing(movement, area, manager):
    assert not can_manage(manager, area)
    assert not can_manage(AnonymousUser(), area)
    assert not manageable_areas(AnonymousUser()).exists()


def test_superuser_manages_everything(movement, area):
    assert can_manage(fresh(movement.director), area)
