from django.core.management.base import BaseCommand
from nest_boxes.help_content import load_help
from nest_boxes.models import HelpArticle, HelpImage


class Command(BaseCommand):
    help = (
        "Fills the nest box help articles that are still empty with the shipped content"
    )

    def handle(self, *args, **options):
        load_help(HelpArticle, HelpImage)
