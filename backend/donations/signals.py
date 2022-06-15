from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from donations.models import VariableSymbol, Donation


@receiver(post_save, sender=VariableSymbol, dispatch_uid='assign_donations_to_donors')
def assign_donations_to_donors(instance: VariableSymbol, **kwargs):
    donations = []
    for donation in Donation.objects.filter(_variable_symbol=instance.variable_symbol):
        donation.donor = instance.donor
        donations.append(donation)

    Donation.objects.bulk_update(donations, ['donor'])


@receiver(post_delete, sender=VariableSymbol, dispatch_uid='remove_donations_from_donors')
def remove_donations_from_donors(instance: VariableSymbol, **kwargs):
    donations = []
    for donation in Donation.objects.filter(_variable_symbol=instance.variable_symbol):
        donation.donor = None
        donations.append(donation)

    Donation.objects.bulk_update(donations, ['donor'])
