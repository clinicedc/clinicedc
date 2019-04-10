from django.core.management.base import BaseCommand, CommandError

from edc_list_data.site_list_data import site_list_data, SiteListDataError


class Command(BaseCommand):

    help = "Populates list data and other static model data from list_data.py"
    module_name = "list_data"

    def handle(self, *args, **options):
        try:
            site_list_data.autodiscover()
        except SiteListDataError as e:
            raise CommandError(e)
