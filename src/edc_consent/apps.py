import copy
import sys

from dateutil.relativedelta import relativedelta
from django.apps import AppConfig as DjangoAppConfig
from django.utils import timezone

from edc_consent.consent import Consent
from edc_consent.site_consents import site_consents


class AppConfig(DjangoAppConfig):
    name = 'edc_consent'
    verbose_name = 'Edc Consent'
    consents = [
        Consent('edc_example.subjectconsent', version='1',
                start=timezone.now() - relativedelta(years=1),
                end=timezone.now() + relativedelta(years=1),
                age_min=16,
                age_is_adult=18,
                age_max=64,
                gender=['M', 'F']),
        Consent('edc_example.subjectconsentproxy', version='1',
                start=timezone.now() - relativedelta(years=1),
                end=timezone.now() + relativedelta(years=1),
                age_min=16,
                age_is_adult=18,
                age_max=64,
                gender=['M', 'F'])
    ]

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        temp = {}
        for consent in self.consents:
            site_consents.register(consent)
            sys.stdout.write(' * registered {}.\n'.format(consent))
            temp[consent.label_lower] = consent
        self.consents = copy.copy(temp)  # convert to dict
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    def get_consent(self, model):
        return self.consents[model]
