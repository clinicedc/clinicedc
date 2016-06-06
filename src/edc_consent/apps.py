import sys

from django.apps import AppConfig
from django.conf import settings
from django.apps import apps as django_apps

from edc_configuration.convert import localize


class EdcConsentAppConfig(AppConfig):
    name = 'edc_consent'
    verbose_name = 'Consent'
    consent_type_setup = None

    def ready(self):
        sys.stdout.write('Loading {} ...\r'.format(self.verbose_name))
        self.update_or_create_consent_type()

    def update_or_create_consent_type(self):
        done_message = 'Loading {} ... Done.\n'.format(self.verbose_name)
        ConsentType = django_apps.get_model(self.name, 'consenttype')
        for item in self.consent_type_setup:
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
