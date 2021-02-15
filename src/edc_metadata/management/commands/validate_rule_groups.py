from django.core.management.base import BaseCommand

from ...site import site_metadata_rules


class Command(BaseCommand):

    help = "Performs a `get_model` for each target models referenced"

    def handle(self, *args, **options):
        site_metadata_rules.validate()
