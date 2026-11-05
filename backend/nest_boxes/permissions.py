def is_manager(user):
    """A budkař or superuser manages every area; nobody else manages any."""
    return user.is_authenticated and (user.is_superuser or user.is_nest_box_manager)
