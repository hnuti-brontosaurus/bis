from nest_boxes.models import Area


def can_manage_all(user):
    """Budkař or superuser: manages every area and creates new ones."""
    return user.is_authenticated and (user.is_superuser or user.is_nest_box_manager)


def manageable_areas(user):
    if not user.is_authenticated:
        return Area.objects.none()
    if can_manage_all(user):
        return Area.objects.all()
    return Area.objects.filter(administration_unit__board_members=user)


def can_manage(user, area):
    return manageable_areas(user).filter(pk=area.pk).exists()
