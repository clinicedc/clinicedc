from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from edc_quota.configure import Configure


class Command(BaseCommand):

    def handle(self, *args, **options):

        pass
