from __future__ import print_function

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):

    args = ''
    help = ('DELETES records in the auth_user_permissions table!. '
            'You need to do this before running update_visit_schedule_permissions.')

    def handle(self, *args, **options):
        Group.permissions.through.objects.all().delete()
        print('All group permissions ManyToMany have been deleted. Run \''
              'python manage.py update_visit_schedue_permissions group_name --app_label app_label\'.')
