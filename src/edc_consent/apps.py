import sys

from django.apps import AppConfig
from django.apps import apps as django_apps
from django.conf import settings
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError

from edc_base.utils.convert import localize


def update_or_create_consent_type(sender, **kwargs):
    sys.stdout.write('Loading {} ...\r'.format(sender.verbose_name))
    done_message = 'Loading {} ... Done.\n'.format(sender.verbose_name)
    ConsentType = django_apps.get_model(sender.name, 'consenttype')
    for item in sender.consent_type_setup:
        if settings.USE_TZ:
            item['start_datetime'] = localize(item.get('start_datetime'))
            item['end_datetime'] = localize(item.get('end_datetime'))
        try:
            consent_type = ConsentType.objects.get(
                version=item.get('version'),
                app_label=item.get('app_label'),
                model_name=item.get('model_name'))
            consent_type.start_datetime = item.get('start_datetime')
            consent_type.end_datetime = item.get('end_datetime')
            consent_type.save()
        except ConsentType.DoesNotExist:
            ConsentType.objects.create(**item)
            done_message = '\n'
            sys.stdout.write('\n * added {}.{} version {}'.format(
                item.get('app_label'), item.get('model_name'), item.get('version')))
    sys.stdout.write(done_message)


class EdcConsentAppConfig(AppConfig):
    name = 'edc_consent'
    verbose_name = 'Consent'
    consent_type_setup = None

    def ready(self):
        try:
            update_or_create_consent_type(self)
        except (OperationalError, ProgrammingError):
            post_migrate.connect(update_or_create_consent_type, sender=self)
