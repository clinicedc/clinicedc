import sys

from django.apps import AppConfig as DjangoAppConfig

from .constants import DEFAULT_CONSENT_GROUP


class AppConfig(DjangoAppConfig):
    name = "edc_consent"
    verbose_name = "Edc Consent"
    default_consent_group = DEFAULT_CONSENT_GROUP
    include_in_administration_section = True

    def ready(self):
        from .site_consents import site_consents

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_consents.autodiscover()
        for consent in site_consents.consents:
            start = consent.start.strftime("%Y-%m-%d %Z")
            end = consent.end.strftime("%Y-%m-%d %Z")
            sys.stdout.write(f" * {consent} covering {start} to {end}\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
