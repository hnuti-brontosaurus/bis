"""The public figures, cached until a box, check or area changes.

Every cached answer is keyed by a generation that a change replaces, so one
cache delete drops them all; the old entries just expire.
"""

from uuid import uuid4

from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from nest_boxes.models import Area, Check, NestBox

GENERATION_KEY = "nest_boxes_public_generation"
# Bounds what the signals miss: a renamed unit, a box type's needs_cleaning
TIMEOUT = 60 * 60


def cached(key, compute):
    generation = cache.get_or_set(GENERATION_KEY, lambda: uuid4().hex, None)
    # A new season starts on 1 July without anything being saved
    full_key = f"nest_boxes_public:{generation}:{Check.current_season()}:{key}"
    return cache.get_or_set(full_key, compute, TIMEOUT)


def invalidate():
    cache.delete(GENERATION_KEY)


@receiver(post_save, sender=NestBox)
@receiver(post_save, sender=Check)
@receiver(post_save, sender=Area)
@receiver(post_delete, sender=NestBox)
@receiver(post_delete, sender=Check)
@receiver(post_delete, sender=Area)
def _invalidate_on_change(**kwargs):
    # Until the commit, a request computing the figures would still see the old rows
    transaction.on_commit(invalidate)
