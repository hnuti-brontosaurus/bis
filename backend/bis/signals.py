from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from vokativ import vokativ

from bis.models import User, Location, UserEmail, Qualification
from project import settings
from regions.models import Region


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid='create_auth_token_for_all_users')
def create_auth_token_for_all_users(instance: User, created, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)


@receiver(pre_save, sender=settings.AUTH_USER_MODEL, dispatch_uid='set_vokativ')
def set_vokativ(instance: User, **kwargs):
    if not instance.vokativ:
        instance.vokativ = vokativ(instance.first_name.split(' ')[0]).capitalize()

        if instance.nickname:
            instance.vokativ = vokativ(instance.nickname).capitalize()


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid='set_unique_str')
def set_unique_str(instance: User, **kwargs):
    data = {'': list(User.objects.all().select_related('address'))}
    new_data = {}

    f1 = lambda user: user.get_name()

    def f2(user):
        _str = [user.get_name()]
        if hasattr(user, 'address') and user.address.city: _str.append(user.address.city)
        if user.age is not None: _str.append(f'{user.age} let')
        return ', '.join(_str)

    for f in [f1, f2]:
        for key, value in data.items():
            if len(value) > 1:
                for user in value:
                    new_data.setdefault(f(user), []).append(user)

            else:
                new_data[key] = value

        new_data, data = data, new_data
        new_data.clear()

    to_update = []
    for key, value in data.items():
        for user in value:
            if user._str != key:
                user._str = key
                to_update.append(user)

    if to_update:
        User.objects.bulk_update(to_update, ['_str'], batch_size=100)


@receiver(post_save, sender=Location, dispatch_uid='set_region_for_location')
def set_region_for_location(instance: Location, created, **kwargs):
    if instance.gps_location:
        region = Region.objects.filter(area__contains=instance.gps_location).first()
        if region != instance.region:
            instance.region = region
            instance.save()


@receiver(pre_save, sender=Qualification, dispatch_uid='set_qualification_end_date')
def set_qualification_end_date(instance: Qualification, **kwargs):
    instance.valid_till = instance.valid_since + relativedelta(years=5)

    if instance.category.slug == "organizer":
        instance.valid_till = date(instance.valid_since.year + 5, 9, 30)

    if instance.category.slug in ['weekend_organizer', 'main_leader_of_kids_camps']:
        instance.valid_till = instance.valid_since + relativedelta(years=100)


@receiver(post_save, sender=User, dispatch_uid='set_primary_email')
def set_primary_email(instance: User, **kwargs):
    email = instance.all_emails.first()
    email = email and email.email
    if email != instance.email:
        if instance.email is not None:
            UserEmail.objects.get_or_create(user=instance, email=instance.email)
            all_emails = sorted(instance.all_emails.all(), key=lambda x: x != instance.email)
            for i, obj in enumerate(all_emails):
                if obj.order != i:
                    obj.order = i
                    obj.save()
        else:
            instance.email = email
            instance.save()


@receiver(post_save, sender=UserEmail, dispatch_uid='set_users_primary_email')
@receiver(post_delete, sender=UserEmail, dispatch_uid='set_users_primary_email_delete')
def set_users_primary_email(instance: UserEmail, **kwargs):
    if cache.get('skip_validation'): return
    first = getattr(instance.user.all_emails.first(), 'email', None)
    if instance.user.email != first:
        instance.user.email = first
        instance.user.save()


class paused_user_str_signal:
    def __enter__(self):
        post_save.disconnect(sender=settings.AUTH_USER_MODEL, dispatch_uid='set_unique_str')

    def __exit__(self, exc_type, exc_val, exc_tb):
        post_save.connect(set_unique_str, sender=settings.AUTH_USER_MODEL, dispatch_uid='set_unique_str')
        User.objects.first().save()


def with_paused_user_str_signal(f):
    def wrapper(*args, **kwargs):
        with paused_user_str_signal():
            return f(*args, **kwargs)

    return wrapper
