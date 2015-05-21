from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from edc_registration.models import RegisteredSubject

from ...models import SubjectIdentifier


class Command(BaseCommand):

    args = '--check <subject_type> --update <subject_type>'
    help = 'Check / Update SubjectIdentifier model from RegisteredSubject Model'
    option_list = BaseCommand.option_list + (
        make_option(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help=('Update SubjectIdentifier. (DATA WILL BE CHANGED.).')), )
    option_list += (
        make_option(
            '--check',
            action='store_true',
            dest='check',
            default=False,
            help=('Check SubjectIdentifier. (Safe).')), )

    def handle(self, *args, **options):
        try:
            subject_type = args[0]
        except:
            raise CommandError('missing parameter <subject_type>')
        if options['check']:
            self.check(subject_type)
        elif options['update']:
            self.update(subject_type)
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')

    def check(self, subject_type):
        self._process(subject_type, 'check')

    def update(self, subject_type):
        self._process(subject_type, 'update')

    def _process(self, subject_type, action):
        n = 0
        tot = RegisteredSubject.objects.filter(
            subject_identifier__isnull=False,
            subject_type=subject_type).count()
        for rs in RegisteredSubject.objects.filter(
                subject_identifier__isnull=False, subject_type=subject_type):
            if not SubjectIdentifier.objects.filter(identifier=rs.subject_identifier).exists():
                n += 1
                print('    {0} / {1} {2}, missing.'.format(n, tot, rs.subject_identifier))
                if action == 'update':
                    SubjectIdentifier.objects.create(identifier=rs.subject_identifier)
                    print('        created')
            else:
                print('    {0} / {1} {2}, found.'.format(n, tot, rs.subject_identifier))
        if action == 'check':
            print(
                '{0} / {1} identifiers NOT found in RegisteredSubject but '
                'not in SubjectIdentifier'.format(n, tot))
        print('Done.')
