from django.core.management.base import BaseCommand

from edc_auth.fix_export_permissions import ExportPermissionsFixer


class Command(BaseCommand):
    def handle(self, *args, **options):
        fixer = ExportPermissionsFixer()
        fixer.fix()
