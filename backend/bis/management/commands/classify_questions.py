from common.sensitivity import classify_unclassified
from django.core.management.base import BaseCommand
from feedback.models import Inquiry
from questionnaire.models import Question


class Command(BaseCommand):
    def handle(self, *args, **options):
        classify_unclassified(Question, "question")
        classify_unclassified(Inquiry, "inquiry")
