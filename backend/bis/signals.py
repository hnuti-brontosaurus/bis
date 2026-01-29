from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from unidecode import unidecode
from vokativ import vokativ

from bis import emails
from bis.models import Location, Qualification, User, UserEmail
from project import settings
from regions.models import Region


@receiver(
    post_save,
    sender=settings.AUTH_USER_MODEL,
    dispatch_uid="create_auth_token_for_all_users",
)
def create_auth_token_for_all_users(instance: User, created, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)


@receiver(pre_save, sender=settings.AUTH_USER_MODEL, dispatch_uid="set_vokativ")
def set_vokativ(instance: User, **kwargs):
    if not instance.vokativ:
        instance.vokativ = vokativ(instance.first_name.split(" ")[0]).capitalize()

        if instance.nickname:
            instance.vokativ = vokativ(instance.nickname).capitalize()


@receiver(pre_save, sender=settings.AUTH_USER_MODEL, dispatch_uid="set__str")
def set__str(instance: User, **kwargs):
    if not instance._str:
        instance._str = instance.get_extended_name()


@receiver(post_save, sender=Location, dispatch_uid="set_region_for_location")
def set_region_for_location(instance: Location, created, **kwargs):
    if instance.gps_location:
        region = Region.objects.filter(area__contains=instance.gps_location).first()
        if region != instance.region:
            instance.region = region
            instance.save()


@receiver(pre_save, sender=Qualification, dispatch_uid="set_qualification_end_date")
def set_qualification_end_date(instance: Qualification, **kwargs):
    instance.valid_till = instance.valid_since + relativedelta(years=5)

    if instance.category.slug == "organizer":
        instance.valid_till = date(instance.valid_since.year + 5, 9, 30)

    if instance.category.slug in ["weekend_organizer", "main_leader_of_kids_camps"]:
        instance.valid_till = instance.valid_since + relativedelta(years=100)


@receiver(post_save, sender=Qualification, dispatch_uid="qualification_created_email")
def qualification_created_email(instance: Qualification, created, **kwargs):
    if created:
        emails.qualification_created(instance)


@receiver(post_save, sender=User, dispatch_uid="set_primary_email")
def set_primary_email(instance: User, **kwargs):
    email = instance.all_emails.first()
    email = email and email.email
    if email != instance.email:
        if instance.email is not None:
            if not instance.all_emails.filter(email=instance.email).exists():
                UserEmail.objects.bulk_create(
                    [UserEmail(user=instance, email=instance.email)]
                )
            all_emails = sorted(
                instance.all_emails.all(), key=lambda x: x.email != instance.email
            )
            for i, obj in enumerate(all_emails):
                if obj.order != i:
                    UserEmail.objects.filter(id=obj.id).update(order=i)
        else:
            instance.email = email
            instance.save()


@receiver(post_save, sender=UserEmail, dispatch_uid="set_users_primary_email")
@receiver(post_delete, sender=UserEmail, dispatch_uid="set_users_primary_email_delete")
def set_users_primary_email(instance: UserEmail, **kwargs):
    if cache.get("skip_validation"):
        return
    first = getattr(instance.user.all_emails.first(), "email", None)
    if instance.user.email != first:
        instance.user.email = first
        instance.user.save()


@receiver(post_save, sender=User, dispatch_uid="update_roles")
def update_roles(instance: User, **kwargs):
    instance.update_roles()
