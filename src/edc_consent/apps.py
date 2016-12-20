import sys

from dateutil.relativedelta import relativedelta

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from edc_base.utils import get_utcnow

from .consent_config import ConsentConfig
from .site_consents import site_consents


class AppConfig(DjangoAppConfig):
    name = 'edc_consent'
    verbose_name = 'Edc Consent'
    consent_configs = [  # don't access directly, use site_consents
        ConsentConfig(
            'edc_example.subjectconsent',
            version='1',
            start=get_utcnow() - relativedelta(years=1),
            end=get_utcnow() + relativedelta(years=1),
            age_min=16,
            age_is_adult=18,
            age_max=64,
            gender=['M', 'F'],
            subject_type='subject'),
    ]

    def ready(self):
        style = color_style()
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        if 'test' in sys.argv:
            sys.stdout.write(
                style.NOTICE(
                    'WARNING! Overwriting AppConfig consent.start and end dates for tests only. \n'
                    'See edc_consent.AppConfig\n'))
            testconsentconfigs = []
            for consent_config in self.consent_configs:
                duration_delta = relativedelta(consent_config.end, consent_config.start)
                consent_config.start = (get_utcnow() - relativedelta(years=1)) - duration_delta
                consent_config.end = get_utcnow() - relativedelta(years=1)
                testconsentconfigs.append(consent_config)
            self.consent_configs = testconsentconfigs
        for consent_config in self.consent_configs:
            site_consents.register(consent_config)
            sys.stdout.write(' * registered {}.\n'.format(consent_config))
            sys.stdout.write('   - consent period {} to {}.\n'.format(
                consent_config.start.strftime('%Y-%m-%d'),
                consent_config.end.strftime('%Y-%m-%d')))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    def get_consent_config(self, model):
        return site_consents.get_consent_config(model)
