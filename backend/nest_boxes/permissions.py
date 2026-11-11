from administration_units.models import AdministrationUnit
from django.db.models import Q
from nest_boxes.models import Area


def manages_all(user):
    """A budkař or superuser: every area, and the help articles."""
    return user.is_authenticated and (user.is_superuser or user.is_nest_box_manager)


def managed_units(user):
    """The units whose areas the user manages: through their board, or as one
    of the unit's own budkaři."""
    if not user.is_authenticated:
        return AdministrationUnit.objects.none()
    if manages_all(user):
        return AdministrationUnit.objects.all()
    return AdministrationUnit.objects.filter(
        Q(pk__in=user.administration_units.values("pk"))
        | Q(pk__in=user.nest_box_units.values("pk"))
    )


def manageable_areas(user):
    if manages_all(user):
        return Area.objects.all()
    return Area.objects.filter(administration_unit__in=managed_units(user))


def can_manage(user, area):
    return manageable_areas(user).filter(pk=area.pk).exists()


def is_manager(user):
    """Manages a unit's areas, possibly none yet: a board creates its first one."""
    return managed_units(user).exists()
