from django.core.management.base import BaseCommand
from edc_crf.update_crf_status import update_crf_status_command


class Command(BaseCommand):
    def handle(self, *args, **options):

        update_crf_status_command(app_label=None)
