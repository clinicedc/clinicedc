from __future__ import print_function

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission


class Command(BaseCommand):

    args = ''
    help = ('DELETES Permissions!. Clears the django Permissions model. '
            'You will need to run syncdb (and comment out south) after.')

    def handle(self, *args, **options):
        Permission.objects.all().delete()
        print('All permissions have been deleted. Run syncdb (without south).')
