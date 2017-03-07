import sys

from django.apps import AppConfig as DjangoAppConfig

from .constants import DEFAULT_CONSENT_GROUP


class AppConfig(DjangoAppConfig):
    name = 'edc_consent'
    verbose_name = 'Edc Consent'
    default_consent_group = DEFAULT_CONSENT_GROUP

    def ready(self):
        from .site_consents import site_consents
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_consents.autodiscover()
        for consent in site_consents.consents:
            sys.stdout.write(' * {} covering {} to {}\n'.format(
                consent, consent.start.strftime('%Y-%m-%d %Z'),
                consent.end.strftime('%Y-%m-%d %Z')))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
