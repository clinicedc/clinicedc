from django.core.management.base import BaseCommand, CommandError

from ...import_holidays import import_holidays, HolidayImportError


class Command(BaseCommand):

    help = "Import country holidays"

    def handle(self, *args, **options):
        try:
            import_holidays(verbose=True)
        except HolidayImportError as e:
            raise CommandError(e)
