import sys

from dateutil.relativedelta import relativedelta
from django.apps import AppConfig as DjangoAppConfig
from django.utils import timezone

from edc_consent.consent_config import ConsentConfig
from edc_consent.site_consents import site_consents


class AppConfig(DjangoAppConfig):
    name = 'edc_consent'
    verbose_name = 'Edc Consent'
    consent_configs = [  # don't access directly, use site_consents
        ConsentConfig(
            'edc_example.subjectconsent',
            version='1',
            start=timezone.now() - relativedelta(years=1),
            end=timezone.now() + relativedelta(years=1),
            age_min=16,
            age_is_adult=18,
            age_max=64,
            gender=['M', 'F']),
    ]

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        for consent_config in self.consent_configs:
            site_consents.register(consent_config)
            sys.stdout.write(' * registered {}.\n'.format(consent_config))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
