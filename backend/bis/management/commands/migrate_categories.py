from django.core.management.base import BaseCommand

from categories.models import EventCategory
from event.models import Event

old_to_new_mapping = {
    "public__volunteering": "volunteering",
    "public__only_experiential": "experiential",
    "internal__section_meeting": "section_meeting",
    "public__club__meeting": "public_educational",
    "public__club__lecture": "public_educational",
    "public__educational__lecture": "public_educational",
    "public__educational__course": "public_educational",
    "public__educational__educational": "public_educational",
    "public__educational__educational_with_stay": "public_educational",
    "public__other__for_public": "public_educational",
    "public__educational__ohb": "internal_educational",
    "public__other__eco_tent": "presentation",
    "public__other__exhibition": "presentation",
    "internal__volunteer_meeting": "internal",
    "internal__general_meeting": "internal",
}


class Command(BaseCommand):
    help = "Migrates event categories for 2026 events from old to new slugs."

    def handle(self, *args, **options):
        new_categories = {
            slug: EventCategory.objects.get(slug=slug)
            for slug in set(old_to_new_mapping.values())
        }

        events = list(Event.objects.filter(start__year=2026).select_related("category"))

        for event in events:
            new_slug = old_to_new_mapping.get(event.category.slug)
            if new_slug is not None:
                event.category = new_categories[new_slug]

        Event.objects.bulk_update(events, ["category"])
