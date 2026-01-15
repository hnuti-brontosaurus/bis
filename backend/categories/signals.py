from administration_units.models import AdministrationUnit
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from event.models import Event
from opportunities.models import Opportunity

from bis.models import Location


@receiver(
    pre_save, sender=settings.AUTH_USER_MODEL, dispatch_uid="set_search_field_User"
)
@receiver(
    pre_save,
    sender=AdministrationUnit,
    dispatch_uid="set_search_field_AdministrationUnit",
)
@receiver(pre_save, sender=Event, dispatch_uid="set_search_field_Event")
@receiver(pre_save, sender=Location, dispatch_uid="set_search_field_Location")
@receiver(pre_save, sender=Opportunity, dispatch_uid="set_search_field_Opportunity")
def set_search_field(instance, **kwargs):
    instance._search_field = instance.get_search_field_value()
