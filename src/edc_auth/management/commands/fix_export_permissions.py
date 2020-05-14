from django.core.management.base import BaseCommand
from edc_auth.fix_export_permissions import fix_export_permissions


class Command(BaseCommand):
    def handle(self, *args, **options):
        fix_export_permissions()
