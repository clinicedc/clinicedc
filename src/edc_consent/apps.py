import sys

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_consent"
    verbose_name = "Edc Consent"
    include_in_administration_section = True

    def ready(self):
        from .site_consents import site_consents

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_consents.autodiscover()
        for consent_definition in site_consents.consent_definitions:
            start = consent_definition.start.strftime("%Y-%m-%d %Z")
            end = consent_definition.end.strftime("%Y-%m-%d %Z")
            sys.stdout.write(f" * {consent_definition} covering {start} to {end}\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
