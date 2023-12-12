from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from donations.models import Donation, Donor, VariableSymbol
from vokativ import vokativ


@receiver(post_save, sender=VariableSymbol, dispatch_uid="assign_donations_to_donors")
def assign_donations_to_donors(instance: VariableSymbol, **kwargs):
    donations = []
    for donation in Donation.objects.filter(_variable_symbol=instance.variable_symbol):
        donation.donor = instance.donor
        donations.append(donation)

    Donation.objects.bulk_update(donations, ["donor"])


@receiver(
    post_delete, sender=VariableSymbol, dispatch_uid="remove_donations_from_donors"
)
def remove_donations_from_donors(instance: VariableSymbol, **kwargs):
    donations = []
    for donation in Donation.objects.filter(_variable_symbol=instance.variable_symbol):
        donation.donor = None
        donations.append(donation)

    Donation.objects.bulk_update(donations, ["donor"])


@receiver(pre_save, sender=Donor, dispatch_uid="set_formal_vokativ")
def set_formal_vokativ(instance: Donor, **kwargs):
    if not instance.formal_vokativ:
        instance.formal_vokativ = vokativ(
            instance.user.last_name.split(" ")[0]
        ).capitalize()
