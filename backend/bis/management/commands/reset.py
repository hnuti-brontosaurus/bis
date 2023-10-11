from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('flush', no_input=False)
        call_command('create_categories')
        call_command('import_regions')
        call_command('import_zip_codes')
        call_command('import_db')
        call_command('merge_users')
        call_command('set_date_joined')
        call_command('import_donations')
        call_command('import_locations')
