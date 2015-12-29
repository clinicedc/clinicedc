from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from ...classes import Permissions
from ...models import VisitDefinition


class Command(BaseCommand):

    args = '<group_name> --visit_codes --app_label --models'
    help = 'Replace permissions for the models in the visit schedule for the given group.'
    option_list = BaseCommand.option_list + (
        make_option(
            '-c', '--visit_codes',
            dest='visit_codes',
            help=('list of visit definition codes separated by comma (no spaces). '
                  '\'all\' will select all visit codes.')))

    option_list += (
        make_option(
            '-a', '--app_label',
            dest='app_label',
            help=('a valid app_label')),
    )

    option_list += (
        make_option(
            '-m', '--models',
            dest='models',
            help=('a list of models separated by comma (no spaces) for the given app_label')),
    )

    option_list += (
        make_option(
            '--replace',
            action='store_true',
            default=False,
            dest='replace',
            help=('DELETES permissions! Replace instead of update. '
                  'Deletes all permissions in group before updating.')),
    )

    def handle(self, *args, **options):
        self.visit_definition_codes = None
        self.app_label = None
        self.models = None
        self.replace = False
        if not args:
            raise CommandError('Please specify a group name or list of group names')
        if options['visit_codes']:
            if options['visit_codes'] == 'all':
                self.visit_definition_codes = [
                    visit_definition.code for visit_definition in VisitDefinition.objects.all()]
            else:
                self.visit_definition_codes = options['visit_codes'].strip().split(',')
        elif options['replace']:
            self.replace = True
        elif options['app_label']:
            self.app_label = options['app_label']
            if options['models']:
                self.models = options['models'].strip('\ ').split(',')
        else:
            pass
        for group_name in args:
            print 'group: {0}'.format(group_name)
            if self.app_label:
                print '  app_label: {0}'.format(self.app_label)
            if self.models:
                print '  models: {0}'.format(self.models)
            if self.visit_definition_codes:
                print '  visit codes: {0}'.format(', '.join(self.visit_definition_codes))
            permissions = Permissions(
                group_name, ['add', 'change'],
                visit_definition_codes=self.visit_definition_codes,
                app_label=self.app_label,
                models=self.models,
                show_messages=True)
            if self.replace:
                permissions.replace()
            else:
                permissions.update()
            print 'Visit definitions have been replaced'
