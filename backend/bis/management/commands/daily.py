from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("create_categories")
        call_command("update_dashboard_items")
        call_command("close_events")
        call_command("record_history")
        call_command("import_locations")
        call_command("import_donations")
