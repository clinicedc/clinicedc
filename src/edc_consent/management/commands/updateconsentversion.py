from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from edc_consent.models.consent_type import ConsentType
from django.core.exceptions import MultipleObjectsReturned


class Command(BaseCommand):

    help = ('Updates the subject consent version field from \'?\'.')

    option_list = BaseCommand.option_list + (
        make_option(
            '--filter',
            action='store_true',
            dest='filter_version',
            default='?',
            help=('Filter update to consents with this version only (default=\'?\'), '
                  ' .e.g. \'None\', \'1.0\', etc.')),
    )

    def add_arguments(self, parser):
        parser.add_argument('filter', nargs='+', type=str)
        parser.add_argument(
            '--filter',
            action='store_true',
            dest='filter_version',
            default='?',
            help=('Filter update to consents with this version only (default=\'?\'), '
                  '.e.g. \'None\', \'1.0\', etc.'))

    def handle(self, *args, **options):
        if options['filter_version']:
            version = options['filter_version']
            if version.lower() == 'none':
                version = None
            elif version == '?':
                pass
            else:
                try:
                    ConsentType.objects.get(version=version)
                except MultipleObjectsReturned:
                    pass
                except ConsentType.DoesNotExist:
                    raise CommandError('Version \'{}\' is not a valid version.'.format(version))
        self.resave_consents(version)

    def resave_consents(self, version):
        models = []
        for consent_type in ConsentType.objects.all().order_by('version'):
            model_class = consent_type.model_class()
            if not model_class._meta.proxy:
                models.append(consent_type.model_class())
        models = list(set(models))
        self.stdout.write('Found consents: {}'.format(', '.join([m._meta.verbose_name for m in models])))
        for model_class in models:
            saved = 0
            pks_by_version = {}
            for consent_type in ConsentType.objects.all().order_by('version'):
                pks_by_version[consent_type.version] = []
            if version:
                consents = model_class.objects.filter(version=version)
            else:
                consents = model_class.objects.all().order_by('version')
            total = consents.count()
            self.stdout.write("Updating {} \'{}\' where version == \'?\' ... ".format(
                total, model_class._meta.verbose_name))
            for consent in consents:
                saved += 1
                consent_type = ConsentType.objects.get_by_consent_datetime(
                    model_class, consent.consent_datetime)
                consent.version = consent_type.version
                pks_by_version[consent.version].append(consent.pk)
                self.stdout.write('{} / {} \r'.format(saved, total))
            for version, pks in pks_by_version.iteritems():
                self.stdout.write("   {} \'{}\' set to version {} ".format(
                    len(pks), model_class._meta.verbose_name, version))
                model_class.objects.filter(pk__in=pks).update(version=version)
        self.stdout.write("Done.")
