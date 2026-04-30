"""Cheap, synchronous Ingredient normalization.

Anything that talks to the network (Groq enrichment) lives in
`cookbook.services.ingredient_enrichment` and is invoked by the API view —
not from a `pre_save` signal. Signals run inside the request thread on every
save (admin, shell, fixtures, ...) and a network call there blocks the
request and hides errors.
"""

from cookbook.models.ingredients import Ingredient
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Ingredient, dispatch_uid="ingredient_normalize_name")
def ingredient_normalize_name(instance: Ingredient, **kwargs):
    instance.name = " ".join(instance.name.split())
    if instance.pk is None and instance.name:
        instance.name = instance.name.lower().capitalize()
