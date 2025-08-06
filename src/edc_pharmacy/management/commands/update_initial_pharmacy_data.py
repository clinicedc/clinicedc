from django.core.management import BaseCommand
from meta_pharmacy.utils import update_initial_pharmacy_data


class Command(BaseCommand):

    def handle(self, *args, **options):
        """This is an example of an initial set of data"""
        update_initial_pharmacy_data()
        print("Done")
