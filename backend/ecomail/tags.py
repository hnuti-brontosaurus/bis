from bis.models import User


def compute_tags(user: User) -> list[str]:
    return [role.name for role in user.roles.all()] + [
        user.get_subscription_status_display()
    ]
