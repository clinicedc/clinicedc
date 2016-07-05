import sys

from django.apps import AppConfig

from edc_consent.consent_type import site_consent_types, ConsentType


class EdcConsentAppConfig(AppConfig):
    name = 'edc_consent'
    verbose_name = 'Consent'
    consent_type_setup = []

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        for item in self.consent_type_setup:
            consent_type = ConsentType(**item)
            site_consent_types.register(consent_type)
            sys.stdout.write(' * registered {}.\n'.format(consent_type))
        sys.stdout.write('{} Done.\n'.format(self.verbose_name))
