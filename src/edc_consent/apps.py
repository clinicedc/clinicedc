import sys

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_consent'
    verbose_name = 'Edc Consent'

    def ready(self):
        from .site_consents import site_consents
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_consents.autodiscover()
        for consent in site_consents.consents:
            sys.stdout.write(' * {} covering {} to {}\n'.format(
                consent, consent.start.strftime('%Y-%m-%d %Z'),
                consent.end.strftime('%Y-%m-%d %Z')))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
